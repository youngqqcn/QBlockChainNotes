#!coding:utf8

# author:yqq
# date:2020/5/11 0011 11:42
# description:    订单消费者     ETH 和 ETH订单处理的实现类
import logging
from datetime import datetime
from decimal import Decimal

import pika
from eth_typing import HexStr, URI
from eth_utils import to_checksum_address
from pika.adapters.blocking_connection import BlockingChannel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web3 import Web3, HTTPProvider

from src.consumers.consumer_base import WithdrawConsumerBase, TransferFuncResponse
from src.config.constant import WITHDRAW_ORDER_EXCHANGE, Q_ETH_ERC_WITHDRAW, ETH_ROUTING_KEY, ERC20_USDT_ROUTING_KEY, \
    RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_USER_NAME, \
    RABBIT_MQ_PASSWORD, RABBIT_MQ_VRIATUAL_HOST, RABBIT_DIRECT_MODE, ERC20_USDT_CONTRACT_ADDRESS, \
    RABBIT_MQ_HEARTBEAT_TIME, RABBIT_BLOCKED_CONNECTION_TIMEOUT, MYSQL_CONNECT_INFO, ETH_FULL_NODE_RPC_URL, ENV_NAME
from src.consumers.consumer_base import TransferFuncResponse
from src.consumers.eth_erc20.eth_transfer_utils import eth_transfer, erc20_transfer
from src.lib.exceptions import BalanceNotEnoughException, InvalidParametersException
from src.lib.pg_utils import round_down
from src.lib.token_abi.abi import EIP20_ABI
from src.model.model import Project, WithdrawConfig


class EthErc20ConsumerImpl(WithdrawConsumerBase):



    def __init__(self):
        super().__init__()

    def init_db_session(self):
        """
        实现父类的抽象方法
        :return:
        """

        # 初始化 数据库session
        engine = create_engine(MYSQL_CONNECT_INFO,
                               pool_size=5, pool_pre_ping=True, pool_recycle=120)
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=True)  #增删改操作 需要手动flush,
        self.session = Session()
        pass

    def init_mq_connect(self):
        """
        实现父类的抽象方法
        :return:
        """
        #  初始化 消息队列
        credentials = pika.PlainCredentials(RABBIT_MQ_USER_NAME, RABBIT_MQ_PASSWORD)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            RABBIT_MQ_IP, RABBIT_MQ_PORT, RABBIT_MQ_VRIATUAL_HOST, credentials,
            heartbeat=RABBIT_MQ_HEARTBEAT_TIME,
            blocked_connection_timeout=RABBIT_BLOCKED_CONNECTION_TIMEOUT
        ))
        connection.channel()

        self.channel = connection.channel()

        assert isinstance(self.channel, BlockingChannel)

        #同一时间, 只接受一条消息
        self.channel.basic_qos( prefetch_count= 1, global_qos=True)

        # 是为了防止没找到queue队列名称报错
        self.channel.exchange_declare(exchange=WITHDRAW_ORDER_EXCHANGE, exchange_type=RABBIT_DIRECT_MODE)
        self.channel.queue_declare(queue=Q_ETH_ERC_WITHDRAW, durable=True)

        # 将队列绑定到交换机,并设置 routing key
        self.channel.queue_bind(exchange=WITHDRAW_ORDER_EXCHANGE, queue=Q_ETH_ERC_WITHDRAW,
                                routing_key=ETH_ROUTING_KEY)
        self.channel.queue_bind(exchange=WITHDRAW_ORDER_EXCHANGE, queue=Q_ETH_ERC_WITHDRAW,
                                routing_key=ERC20_USDT_ROUTING_KEY)

        # 设置绑定队列,设置回调函数
        self.channel.basic_consume(queue=Q_ETH_ERC_WITHDRAW,
                                   on_message_callback=self.on_message_callback,  # 调用父类的方法,
                                   auto_ack=False)  # 如果接收消息，机器宕机消息就丢了
        pass

    def init_others(self):
        """
        实现父类抽象方法
        :return:
        """

        #  初始化 logger

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d | %(levelname)s - %(message)s')

        self.logger = logging.getLogger(__name__)



        pass

    def check_src_address_balance(self, **kwargs) -> bool:

        token_name = kwargs['token_name']
        from_addr = kwargs['from_addr']
        # to_addr = kwargs['to_addr']
        amount = kwargs['amount']  # 特别注意: 以 ETH 为单位, 不要转为 wei !!!
        # priv_key = kwargs['priv_key']
        pro_id = kwargs['pro_id']

        project = self.session.query(Project).filter_by(pro_id=pro_id).first()
        assert isinstance(project, Project), f'not found pro_id:{pro_id} in project'


        eth_withdraw_cfg = self.session.query(WithdrawConfig).filter_by(pro_id=pro_id, token_name='ETH').first()
        assert isinstance(eth_withdraw_cfg, WithdrawConfig) , f'not found pro_id:{pro_id} in withdraw_cfg'

        amount = round_down(amount)

        block_identifier = HexStr('latest')  # 不能用pending
        myweb3 = Web3(provider=HTTPProvider(endpoint_uri=URI(ETH_FULL_NODE_RPC_URL)))
        nbalance = myweb3.eth.getBalance(account=to_checksum_address(from_addr), block_identifier=block_identifier)
        ether_balance = myweb3.fromWei(nbalance, 'ether')  # ETH 余额

        decim_eth_balance = round_down(ether_balance)

        sms_content = ''
        sms_template = '【shbao】 尊敬的管理员，余额预警。{0}出币地址{1}余额为{2}，请立即充值{3}。{4},{5}' +  f',{project.pro_name}'

        try:
            if token_name == 'ETH':
                if decim_eth_balance < amount + Decimal('0.01'):
                    str_balance = ('%.8f' % decim_eth_balance)  if decim_eth_balance > Decimal('0.00000001') else '0'
                    self.logger.error(f'ETH balance {str_balance } < {amount + Decimal("0.01")}')
                    sms_content = sms_template.format('ETH', 'ETH', str_balance, 'ETH', str(datetime.now()), ENV_NAME.upper() )
                    raise BalanceNotEnoughException(sms_content)

                #如果当前余额小于设定的预警值 则发送短信通知项目方
                if decim_eth_balance < eth_withdraw_cfg.balance_threshold_to_sms:
                    sms_content = sms_template.format('ETH', 'ETH', decim_eth_balance, 'ETH', str(datetime.now()), ENV_NAME.upper() )
            else:  # USDT交易
                usdt_withdraw_cfg = self.session.query(WithdrawConfig).filter_by(pro_id=pro_id,
                                                                                 token_name='USDT').first()
                assert isinstance(usdt_withdraw_cfg, WithdrawConfig), f'not found pro_id:{pro_id} in withdraw_cfg'

                if decim_eth_balance < Decimal('0.01'):
                    str_balance = ('%.8f' % decim_eth_balance) if decim_eth_balance > Decimal('0.00000001') else '0'
                    self.logger.error(f'ETH balance {str_balance} < 0.01')
                    sms_content = sms_template.format('USDT', 'ETH手续费', str_balance, 'ETH', str(datetime.now()), ENV_NAME.upper() )
                    raise BalanceNotEnoughException(sms_content)

                chksum_contract_addr = to_checksum_address(ERC20_USDT_CONTRACT_ADDRESS)
                contract = myweb3.eth.contract(address=chksum_contract_addr, abi=EIP20_ABI)
                # symbol = contract.functions.symbol().call()
                # decimals = contract.functions.decimals().call()
                erc20_token_balance_int = contract.functions.balanceOf(to_checksum_address(from_addr)).call()
                if erc20_token_balance_int == 0:
                    self.logger.error(f'token balance is 0')
                    sms_content = sms_template.format('USDT', 'USDT', 0, 'USDT', str(datetime.now()), ENV_NAME.upper())
                    raise BalanceNotEnoughException(sms_content)

                erc20_token_balance_decimal = myweb3.fromWei(erc20_token_balance_int, unit='mwei')
                token_balance = round_down(erc20_token_balance_decimal)
                if token_balance < amount + Decimal('0.1'):
                    self.logger.error(f'token balance {token_balance} < {amount + Decimal("0.1")}')
                    sms_content = sms_template.format('USDT', 'USDT', token_balance, 'USDT', str(datetime.now()), ENV_NAME.upper() )
                    raise BalanceNotEnoughException(sms_content)

                # 如果当前余额小于设定的预警值 则发送短信通知项目方
                if token_balance < usdt_withdraw_cfg.balance_threshold_to_sms:
                    sms_content = sms_template.format('USDT', 'USDT', token_balance, 'USDT', str(datetime.now()), ENV_NAME.upper() )

        except BalanceNotEnoughException as e:
            tel_no = project.tel_no
            self.send_sms_queue(sms_content=sms_content, tel_no=tel_no)
            self.logger.info('send_sms_queue finished')
            raise e

        #发送余额预警短信
        if len(sms_content) != 0:
            tel_no = project.tel_no
            self.send_sms_queue(sms_content=sms_content, tel_no=tel_no)
            self.logger.info('send_sms_queue finished')

        return  True


    # 实现父类的抽象方法
    def transfer(self, **kwargs) -> TransferFuncResponse:

        token_name = kwargs['token_name']
        from_addr = kwargs['from_addr']
        to_addr = kwargs['to_addr']
        amount = kwargs['amount']   #特别注意: 以 ETH 为单位, 不要转为 wei !!!
        priv_key = kwargs['priv_key']

        if str(token_name).upper() == 'ETH':
            return eth_transfer(priv_key=priv_key, from_addr=from_addr, to_addr=to_addr, amount=amount)
        elif str(token_name).upper() == 'USDT':
            return erc20_transfer(priv_key=priv_key, from_addr=from_addr,
                           contract_addr=ERC20_USDT_CONTRACT_ADDRESS,
                           token_recipient_addr=to_addr,
                            token_amount=amount)
        else:
            raise Exception(f"invalid token_name:{token_name}")



