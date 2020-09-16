#!coding:utf8

#author:yqq
#date:2020/5/13 0013 18:27
#description:  扫描
import abc
import time
import typing
from typing import List

from redis import Redis
from sqlalchemy.dialects.mysql import Insert, insert
from sqlalchemy.ext.declarative import declarative_base

from src.config.constant import REDIS_DEPOSIT_ADDRESS_POOL_NAME
from src.model.model import ScanStartBlock, Deposit, Address
import traceback


class ScannerBase(metaclass=abc.ABCMeta):

    logger = None  # 日志
    session = None  # 数据库
    redis : Redis  = None   #redis连接
    token_name : str = None  #币名
    block_count_to_wait_confirm : int = None  #最小确认数, ETH是12个, HTDF是1个

    @abc.abstractmethod
    def __init__(self):
        """
        抽象方法, 子类必须实现,  并对成员变量进行初始化
        """
        pass


    def  load_address_to_cache(self, redis_key_name : str = REDIS_DEPOSIT_ADDRESS_POOL_NAME):
        """
        抽象方法, 子类必须实现,
        加载充币地址到缓存中,  扫描模块根据缓存中的地址进行交易监控
        :return:
        """

        ret_addrs = self.session.query(Address.address).filter_by(token_name=self.token_name).all()

        addrs_list = []
        for addr in ret_addrs:
            addrs_list.append(addr.address)

        if len(addrs_list) == 0:
            err_msg  = f'NOT FOUND ANY ADDRESS FROM DB, TO LOADING INTO REDIS!  在数据库中未找到任何充币地址,需要加载到redis中!'
            self.logger.warning(err_msg)
            # raise Exception(err_msg)
        else:
            self.logger.info(f'loading {len(addrs_list)} to redis.')
            self.redis.sadd(redis_key_name, *tuple(addrs_list))
            self.logger.info(f'loaded {len(addrs_list)} address to redis finished.')

        pass

    @abc.abstractmethod
    def refresh_deposit_address_balance(self, address : str) -> bool:
        """
        抽象方法, 子类必须实现
        刷新  tb_active_address_balances 中地址的余额
        :param address:  地址
        :return: 成功  True,  失败 False
        """
        pass

    @abc.abstractmethod
    def get_latest_block_height_from_blockchain(self) -> int:
        """
        抽象方法, 子类必须实现
        获取区块链上的最新的区块高度
        :return:
        """
        pass


    @abc.abstractmethod
    def get_deposit_transactions_from_block(self, height : int) -> List[Deposit]:
        """
        从某个区块中获取充币交易
        :param height:  区块高度
        :return:  list[Deposit]
        """
        pass

    def get_scan_start_height(self, token_name : str) -> int:
        """
        从数据库的  tb_scan_start_height 表中获取扫描的起始高度
        :param token_name: 币名
        :return: 高度
        """
        result = self.session.query(ScanStartBlock.block_height) \
            .filter_by(token_name=token_name.upper()) \
            .first()

        # 如果查询不到, first() 返回None
        if result is None:
            error_msg = f"=====>ERROR=====> get {token_name} start height failed!!!"
            self.logger.critical(error_msg)
            raise Exception(error_msg)

        self.logger.info(f'get {token_name} start height: {result.block_height}')
        return result.block_height


    def update_scan_start_height(self, token_name : str, height : int) -> bool:
        """
        更新  tb_scan_start  的高度
        :param token_name: 币名
        :param height: 高度
        :return: boolean
        """
        ret = self.session.query(ScanStartBlock) \
            .filter_by(token_name=token_name.strip().upper()) \
            .update({
            'block_height': height
        })
        self.session.flush()

        if ret != 1:
            self.logger.error(f'update_scan_start_height({height}) FAILED !')
            return False

        self.logger.info(f'update_scan_start_height({height}) ok!')
        return True


    def is_in_address_cache(self, address: str, redis_key_name : str = REDIS_DEPOSIT_ADDRESS_POOL_NAME) -> bool:
        """
        判断地址是否 在缓存 地址池中
        :param address:
        :return: 存在 True, 不存在 False
        """
        is_member = self.redis.sismember(redis_key_name,  address)
        return is_member



    def upsert(self, model: declarative_base, data: typing.Union[typing.Dict, typing.List[typing.Dict]],
               update_field: typing.List) -> Insert:
        """
        解决 唯一索引冲突的问题
        on_duplicate_key_update for mysql
        """
        # https://docs.sqlalchemy.org/en/13/dialects/mysql.html#insert-on-duplicate-key-update-upsert
        stmt = insert(model).values(data)
        d = {f: getattr(stmt.inserted, f) for f in update_field}
        return stmt.on_duplicate_key_update(**d)


    def start_loop(self):

        assert  self.logger is not  None,  'self.logger is None'
        assert  self.token_name in  ['BTC', 'HTDF', 'ETH'],  'self.token_name is invalid'
        assert  self.redis is not  None,  'self.redis is None'
        assert  self.session is not None , 'self.session is None'
        assert  self.block_count_to_wait_confirm is not None,  'self.block_count_to_wait_confirm is None'

        #0) 将充币地址加载到 redis 中
        self.load_address_to_cache()

        while True:
            try:
                #1) 获取区块链上的最新高度
                latest_height = self.get_latest_block_height_from_blockchain()

                #2) 获取上次扫描的结束高度, 作为本次扫描的起始高度
                scan_start = self.get_scan_start_height(self.token_name)

                #3) 本次扫描的结束高度
                scan_end = latest_height - self.block_count_to_wait_confirm

                #4) 如果起始高度 大于  结束高度 , 本次不扫描
                if scan_start > scan_end:
                    self.logger.info(f'scan_start:{scan_start} > scan_end:{scan_end}')
                    time.sleep(10)
                    continue


                #防止中途失败

                if self.token_name == 'BTC' :
                    scan_end = scan_start + 1  #BTC主网扫描比较慢,一次扫一个区块即可
                elif scan_end == scan_start:
                    scan_end = scan_start + 1
                elif scan_end - scan_start > 10:
                    scan_end = scan_start + 10


                #5) 开始扫描区块
                self.logger.info(f'starting scan  {scan_start} to {scan_end}')
                for n in range(scan_start, scan_end ):

                    #6) 获取一个区块里面所有的充币交易
                    self.logger.info(f'scanning block {n}')
                    all_deposit_txs = self.get_deposit_transactions_from_block(height=n)
                    self.logger.info( f'found {len(all_deposit_txs)} tx' )

                    #7) 将所有充币交易插入数据库
                    for deposit_tx in all_deposit_txs:
                        # sqlret = self.session.merge(instance=deposit_tx, load=True)  #TODO:处理 唯一索引重复

                        data = {
                            'to_addr' : deposit_tx.to_addr,
                            'token_name': deposit_tx.token_name,
                            'pro_id': deposit_tx.pro_id,
                            'block_height' : deposit_tx.block_height,
                            'from_addr' : deposit_tx.from_addr,
                            'tx_hash' : deposit_tx.tx_hash ,
                            'block_time' : deposit_tx.block_time,
                            'notify_status' : deposit_tx.notify_status,
                            'amount' : deposit_tx.amount,
                            'memo' : deposit_tx.memo,
                            'tx_confirmations' : deposit_tx.tx_confirmations + 2,
                        }

                        #如果已经存在,则只更新确认数即可
                        update_fields = ['tx_confirmations']
                        stmt  = self.upsert(Deposit,  data=data, update_field=update_fields )

                        sqlret = self.session.execute(stmt)
                        self.logger.info(f'-------->sql-----> {sqlret}')
                        sqlret =  self.session.flush()
                        self.logger.info(f'-------->sql-----> {sqlret}')
                        # self.logger.info('----')

                #8) 更新扫描记录表,保存本次扫描的结束区块高度, 方便下次
                self.update_scan_start_height(token_name=self.token_name, height=scan_end) #下次直接从scan_end开始

                if (latest_height - scan_end) == self.block_count_to_wait_confirm:
                    time.sleep(10)

            except Exception as e:
                traceback.print_exc()
                self.logger.error(f'error: {e}')
                time.sleep(5)

        pass









