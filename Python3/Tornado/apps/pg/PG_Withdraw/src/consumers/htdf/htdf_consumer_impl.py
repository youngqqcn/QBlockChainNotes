#!coding:utf8

#author:yqq
#date:2020/5/11 0011 12:55
#description:
import logging
import time
from datetime import datetime
from decimal import Decimal

import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.consumers.consumer_base import WithdrawConsumerBase
from src.config.constant import WITHDRAW_ORDER_EXCHANGE, \
    RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_USER_NAME, \
    RABBIT_MQ_PASSWORD, RABBIT_MQ_VRIATUAL_HOST, RABBIT_DIRECT_MODE, Q_HTDF_WITHDRAW, HTDF_ROUTING_KEY, WithdrawStatus, \
    MYSQL_CONNECT_INFO, HTDF_NODE_RPC_HOST, HTDF_NODE_RPC_PORT, RABBIT_MQ_HEARTBEAT_TIME, \
    RABBIT_BLOCKED_CONNECTION_TIMEOUT, ENV_NAME, HRC20_BTU_ROUTING_KEY, HRC20_CONTRACT_MAP
from src.consumers.consumer_base import TransferFuncResponse
from src.consumers.htdf.cosmos_proxy import CosmosProxy, BadConnectionError
from src.consumers.htdf.htdf_transfer_utils import htdf_transfer, hrc20_transfer
from src.lib.exceptions import InvalidParametersException, HttpConnectionError, BalanceNotEnoughException
from src.lib.pg_utils import round_down
from src.model.model import Project, WithdrawConfig


class HTDFConsumerImpl(WithdrawConsumerBase):


    def init_db_session(self):
        # 2) 初始化 数据库session
        engine = create_engine(MYSQL_CONNECT_INFO,
                               pool_size=5, pool_pre_ping=True, pool_recycle=120)
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)
        self.session = Session()
        pass

    def init_mq_connect(self):


        #3) 初始化 消息队列
        credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
                                RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials,
                    heartbeat = RABBIT_MQ_HEARTBEAT_TIME,
                    blocked_connection_timeout = RABBIT_BLOCKED_CONNECTION_TIMEOUT
        ))

        self.channel = connection.channel()

        # 同一时间, 只接受一条消息
        self.channel.basic_qos(prefetch_count=1, global_qos=True)

        # 是为了防止没找到queue队列名称报错
        self.channel.exchange_declare(exchange=WITHDRAW_ORDER_EXCHANGE, exchange_type=RABBIT_DIRECT_MODE)
        self.channel.queue_declare(queue=Q_HTDF_WITHDRAW, durable=True)

        #将队列绑定到交换机,并设置 routing key
        self.channel.queue_bind(exchange=WITHDRAW_ORDER_EXCHANGE, queue=Q_HTDF_WITHDRAW,
                                routing_key=HTDF_ROUTING_KEY)
        self.channel.queue_bind(exchange=WITHDRAW_ORDER_EXCHANGE, queue=Q_HTDF_WITHDRAW,
                                routing_key=HRC20_BTU_ROUTING_KEY)


        # 设置绑定队列,设置回调函数
        self.channel.basic_consume(queue=Q_HTDF_WITHDRAW,
                                   on_message_callback=self.on_message_callback, #调用父类的方法,
                                   auto_ack=False)  # 如果接收消息，机器宕机消息就丢了

        pass

    def init_others(self):

        #1) 初始化 logger

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d | %(levelname)s - %(message)s')

        self.logger = logging.getLogger(__name__)
        pass


    def check_src_address_balance(self, **kwargs) -> bool:

        token_name = kwargs['token_name']
        from_addr = kwargs['from_addr']
        # to_addr = kwargs['to_addr']
        amount = kwargs['amount']  # 特别注意
        amount = round_down( amount )
        pro_id = kwargs['pro_id']

        project = self.session.query(Project).filter_by(pro_id=pro_id).first()
        assert isinstance(project, Project), f'not found pro_id:{pro_id} in project'

        htdf_withdraw_cfg = self.session.query(WithdrawConfig).filter_by(pro_id=pro_id, token_name='HTDF').first()
        assert isinstance(htdf_withdraw_cfg, WithdrawConfig), f'not found pro_id:{pro_id} in withdraw_cfg'


        rpc = CosmosProxy(host=HTDF_NODE_RPC_HOST, port=HTDF_NODE_RPC_PORT, cointype=token_name)

        sms_content = ''
        sms_template = '【shbao】 尊敬的管理员，余额预警。{0}出币地址{1}余额为{2}，请立即充值{3}。{4},{5}' + f',{project.pro_name}'
        try:
            if token_name == 'HTDF':
                strbalance = rpc.getBalance(from_addr)  # 获取余额

                decim_balance = Decimal(strbalance)
                if decim_balance < amount + Decimal('0.1'):
                    self.logger.error(f'HTDF balance {decim_balance} < {amount + Decimal("0.1")}')
                    sms_content = sms_template.format('HTDF', 'HTDF', decim_balance, 'HTDF', str(datetime.now()),
                                                      ENV_NAME.upper())
                    raise BalanceNotEnoughException(sms_content)

                if decim_balance < htdf_withdraw_cfg.balance_threshold_to_sms:
                    sms_content = sms_template.format('HTDF', 'HTDF', decim_balance, 'HTDF', str(datetime.now()),
                                                      ENV_NAME.upper())
            else: #HRC20
                hrc20_contract = ''
                hrc20_decimals = 18
                for con_addr, sym_info in HRC20_CONTRACT_MAP.items():
                    if sym_info['symbol'] == token_name:
                        hrc20_contract = con_addr
                        hrc20_decimals = sym_info['decimal']

                assert  len(hrc20_contract) == 43,  'hrc20_contract is illegal'
                assert  hrc20_decimals == 18, 'hrc20_deciaml not equal 18'

                hrc20_btu_withdraw_cfg = self.session.query(WithdrawConfig)\
                                        .filter_by(pro_id=pro_id, token_name=token_name).first()
                assert isinstance(hrc20_btu_withdraw_cfg, WithdrawConfig), f'not found pro_id:{pro_id} in withdraw_cfg'

                htdf_balance = rpc.getBalance(from_addr)  # 获取余额
                htdf_decim_balance = Decimal(htdf_balance)
                if htdf_decim_balance < Decimal('0.3'):
                    str_balance = ('%.8f' % htdf_decim_balance) if htdf_decim_balance > Decimal('0.00000001') else '0'
                    self.logger.error(f'HTDF fee balance {str_balance} < 0.01')
                    sms_content = sms_template.format(token_name, 'HTDF手续费', str_balance, 'HTDF', str(datetime.now()),
                                                      ENV_NAME.upper())
                    raise BalanceNotEnoughException(sms_content)


                strbalance = rpc.getHRC20TokenBalance(contract_addr=hrc20_contract, address=from_addr)
                token_balance  = round_down( Decimal(strbalance) )
                if token_balance < amount + Decimal('0.1'):
                    self.logger.error(f'token balance {token_balance} < {amount + Decimal("0.1")}')
                    str_balance = ('%.8f' % token_balance) if token_balance > Decimal('0.00000001') else '0'
                    sms_content = sms_template.format(token_name, token_name, str_balance, token_name, str(datetime.now()),
                                                      ENV_NAME.upper())
                    raise BalanceNotEnoughException(sms_content)

                # 如果当前余额小于设定的预警值 则发送短信通知项目方
                if token_balance < hrc20_btu_withdraw_cfg.balance_threshold_to_sms:
                    sms_content = sms_template.format(token_name, token_name, token_balance, token_name, str(datetime.now()),
                                                      ENV_NAME.upper())


        except BadConnectionError as e:
            self.logger.error(f'connection HTDF node error: {e}')
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


    # 实现父类的抽象方法
    def transfer(self, **kwargs) -> TransferFuncResponse:
        token_name = kwargs['token_name']
        from_addr = kwargs['from_addr']
        to_addr = kwargs['to_addr']
        amount = kwargs['amount']  # 特别注意: 以 HTDF 为单位, 不要转为 satoshi !!!, HRC20则以最大单位计数 !
        priv_key = kwargs['priv_key']
        memo = kwargs['memo']

        if str(token_name).upper() not in ['HTDF', 'BTU']:
            logging.error(f"invalid token_name:{token_name}")
            raise InvalidParametersException(f"invalid token_name:{token_name}")
        try:
            time.sleep(5)  #减少 HTDF频率高时   广播失败的概率
            if token_name == 'HTDF':
                retdata = htdf_transfer(priv_key=priv_key, from_addr=from_addr,
                                    to_addr=to_addr, amount_in_htdf=amount, memo=memo)
            else:
                hrc20_contract = ''
                hrc20_decimals = 18
                for con_addr, sym_info in HRC20_CONTRACT_MAP.items():
                    if sym_info['symbol'] == token_name:
                        hrc20_contract = con_addr
                        hrc20_decimals = sym_info['decimal']

                assert len(hrc20_contract) == 43, 'hrc20_contract is illegal'
                assert hrc20_decimals == 18, 'hrc20_deciaml not equal 18'

                retdata = hrc20_transfer(priv_key=priv_key, from_addr=from_addr,
                                        contract_addr=hrc20_contract, token_recipient=to_addr,
                                         token_amount=amount, token_decimal=hrc20_decimals, memo=memo)
            return retdata
        except ConnectionError as e:
            logging.error(f'connection error : {e}')
            raise HttpConnectionError(e)
        pass