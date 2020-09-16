#!coding:utf8

#author:yqq
#date:2020/7/10 0010 14:03
#description: BTC提币消费实现

import logging
import time
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
import platform

import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.consumers.btc.btc_proxy import BTCProxy
from src.consumers.btc.btc_transfer_utils import BTCTransferUitl
from src.consumers.consumer_base import WithdrawConsumerBase
from src.config.constant import WITHDRAW_ORDER_EXCHANGE, \
    RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_USER_NAME, \
    RABBIT_MQ_PASSWORD, RABBIT_MQ_VRIATUAL_HOST, RABBIT_DIRECT_MODE, Q_HTDF_WITHDRAW, HTDF_ROUTING_KEY, WithdrawStatus, \
    MYSQL_CONNECT_INFO, HTDF_NODE_RPC_HOST, HTDF_NODE_RPC_PORT, RABBIT_MQ_HEARTBEAT_TIME, \
    RABBIT_BLOCKED_CONNECTION_TIMEOUT, ENV_NAME, Q_BTC_WITHDRAW, BTC_ROUTING_KEY, BTC_API_HOST, BTC_API_PORT, \
    g_IS_MAINNET
from src.consumers.consumer_base import TransferFuncResponse
from src.consumers.htdf.cosmos_proxy import CosmosProxy, BadConnectionError
from src.consumers.htdf.htdf_transfer_utils import htdf_transfer
from src.lib.exceptions import InvalidParametersException, HttpConnectionError, BalanceNotEnoughException
from src.lib.pg_utils import round_down
from src.model.model import Project, WithdrawConfig



BTC_TX_FEE = Decimal('0.0002')


class BtcConsumerImpl(WithdrawConsumerBase):

    def init_db_session(self):
        # 2) 初始化 数据库session
        engine = create_engine(MYSQL_CONNECT_INFO,
                               pool_size=5, pool_pre_ping=True, pool_recycle=120)
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)
        self.session = Session()
        pass

    def init_mq_connect(self):
        # 3) 初始化 消息队列
        credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials,
            heartbeat=RABBIT_MQ_HEARTBEAT_TIME,
            blocked_connection_timeout=RABBIT_BLOCKED_CONNECTION_TIMEOUT
        ))

        self.channel = connection.channel()

        # 同一时间, 只接受一条消息
        self.channel.basic_qos(prefetch_count=1, global_qos=True)

        # 是为了防止没找到queue队列名称报错
        self.channel.exchange_declare(exchange=WITHDRAW_ORDER_EXCHANGE, exchange_type=RABBIT_DIRECT_MODE)
        self.channel.queue_declare(queue=Q_BTC_WITHDRAW, durable=True)

        # 将队列绑定到交换机,并设置 routing key
        self.channel.queue_bind(exchange=WITHDRAW_ORDER_EXCHANGE, queue=Q_BTC_WITHDRAW,
                                routing_key=BTC_ROUTING_KEY)

        # 设置绑定队列,设置回调函数
        self.channel.basic_consume(queue=Q_BTC_WITHDRAW,
                                   on_message_callback=self.on_message_callback,  # 调用父类的方法,
                                   auto_ack=False)  # 如果接收消息，机器宕机消息就丢了

        pass


    def init_others(self):
        # 1) 初始化 logger

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d | %(levelname)s - %(message)s')

        self.logger = logging.getLogger(__name__)

        # sysstr = platform.system()
        # global BTC_API_PORT
        # BTC_API_PORT = BTC_API_PORT
        # if (sysstr == "Windows"):
        #     BTC_API_PORT = 3002
        self.proxy = BTCProxy(host=BTC_API_HOST, port=BTC_API_PORT)
        self.btcutil = BTCTransferUitl(host=BTC_API_HOST, port=BTC_API_PORT, net_type='mainnet' if g_IS_MAINNET else 'testnet')


        pass



    def check_src_address_balance(self, **kwargs) -> bool:
        token_name = kwargs['token_name']
        from_addr = kwargs['from_addr']
        # to_addr = kwargs['to_addr']
        amount = kwargs['amount']  # 特别注意
        amount = round_down(amount)
        pro_id = kwargs['pro_id']

        project = self.session.query(Project).filter_by(pro_id=pro_id).first()
        assert isinstance(project, Project), f'not found pro_id:{pro_id} in project'

        btc_withdraw_cfg = self.session.query(WithdrawConfig).filter_by(pro_id=pro_id, token_name='BTC').first()
        assert isinstance(btc_withdraw_cfg, WithdrawConfig), f'not found pro_id:{pro_id} in withdraw_cfg'

        sms_content = ''
        sms_template = '【shbao】 尊敬的管理员，余额预警。{0}出币地址{1}余额为{2}，请立即充值{3}。{4},{5}' + f',{project.pro_name}'
        try:
            assert self.proxy.ping() == True, 'bitcoind rpc is gone'


            # 获取余额(包含未确认的收币, 减去未确认的出币)
            balance_in_satoshi = self.proxy.get_balance(address=from_addr, mem_spent=True, mem_recv=True )
            balance_in_btc = round_down(Decimal(balance_in_satoshi) / Decimal(10 ** 8))

            decim_balance = balance_in_btc
            if decim_balance < amount + BTC_TX_FEE:
                self.logger.error(f'BTC balance {decim_balance} < {amount + BTC_TX_FEE}')
                sms_content = sms_template.format('BTC', 'BTC', decim_balance, 'BTC', str(datetime.now()),
                                                  ENV_NAME.upper())
                raise BalanceNotEnoughException(sms_content)

            if decim_balance < btc_withdraw_cfg.balance_threshold_to_sms:
                sms_content = sms_template.format('BTC', 'BTC', decim_balance, 'BTC', str(datetime.now()),
                                                  ENV_NAME.upper())

        except BadConnectionError as e:
            self.logger.error(f'connection BTC API server error: {e}')
            raise HttpConnectionError(e)
        except BalanceNotEnoughException as e:
            tel_no = project.tel_no
            self.send_sms_queue(sms_content=sms_content, tel_no=tel_no)
            raise e

        # 发送余额预警短信
        if len(sms_content) != 0:
            tel_no = project.tel_no
            self.send_sms_queue(sms_content=sms_content, tel_no=tel_no)

        return True




    def transfer(self, **kwargs) -> TransferFuncResponse:
        token_name = kwargs['token_name']
        from_addr = kwargs['from_addr']
        to_addr = kwargs['to_addr']
        amount = kwargs['amount']  # 以 BTC为单位 , 不是以satoshi为单位
        priv_key = kwargs['priv_key'] # 十六进制字符串格式的私钥

        if str(token_name).upper() != 'BTC':
            logging.error(f"invalid token_name:{token_name}")
            raise InvalidParametersException(f"invalid token_name:{token_name}")
        try:
            src_map = OrderedDict()
            src_map[from_addr] = priv_key

            dst_map = OrderedDict()
            dst_map[to_addr] = Decimal(amount)

            txfee = BTC_TX_FEE

            txid = self.btcutil.transfer(src_addrs_key_map=src_map,
                                  dst_addrs_amount_map=dst_map,
                                  txfee=txfee,
                                  auto_calc_pay_back=True,
                                  pay_back_index=0,
                                  ensure_one_txout=False)

            retdata = TransferFuncResponse()
            retdata.transaction_status = WithdrawStatus.transaction_status.PENDING  # 广播出去了, 就是pending
            retdata.confirmations = 0
            retdata.block_height = 0
            retdata.tx_hash = txid
            return retdata
        except ConnectionError as e:
            logging.error(f'connection error : {e}')
            raise HttpConnectionError(e)

        pass


def main():



    pass


if __name__ == '__main__':

    main()