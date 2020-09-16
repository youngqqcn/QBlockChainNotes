#!coding:utf8

#author:yqq
#date:2020/4/30 0030 19:06
#description:    这里写  ORM的  model


# 数据库操作使用 ORM
#可以参考: https://blog.csdn.net/qq_36019490/article/details/96883453
import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index, DECIMAL, BigInteger

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

ORMBase = declarative_base()

class Project(ORMBase) :
    """
    项目方表
    """

    __tablename__ = 'tb_project'

    pro_id =  Column(key='pro_id', type_=Integer(), nullable=False, primary_key=True, autoincrement=True, comment='项目方id')
    pro_name = Column(key='pro_name', type_=String(50),  nullable=False ,comment='项目方名称')
    tel_no = Column(key='tel_no', type_=String(20),  nullable=False, comment='项目方电话号码')
    email = Column(key='email', type_=String(20), nullable=False, comment='项目方邮箱')
    api_key = Column(key='api_key', type_=String(64), nullable=False, comment='项目方的API_KEY')
    account_status = Column(key='account_status', type_= Integer(),  nullable=False, comment='账户状态, 0:未激活, 1:正常 , 2:已冻结 , 3:已禁用' )
    bip44_account_index = Column(key='bip44_account_index', type_= Integer(), nullable=False, comment='BIP44的账户索引,正常情况下,此值和pro_id相等' )
    create_time = Column(key='create_time', type_=DateTime(timezone=True) , nullable=False, comment='创建时间')

    client_sign_key = Column(key='client_sign_key', type_=String(100),  nullable=False ,comment='客户端私钥')
    client_verify_key = Column(key='client_verify_key', type_=String(100),  nullable=False ,comment='客户端公钥')
    server_sign_key = Column(key='server_sign_key', type_=String(100),  nullable=False ,comment='服务端私钥')
    server_verify_key = Column(key='server_verify_key', type_=String(100),  nullable=False ,comment='服务端公钥')


    def __repr__(self):
        #TODO: 将其他字段也打印出来
        return f"Project(pro_id={self.pro_id}, name={self.pro_name}, tel_no={self.tel_no}, ....)"


class Deposit(ORMBase):
    """
    充币表
    """

    __tablename__ = 'tb_deposit'

    id = Column(key='id', type_=Integer(), primary_key=True, autoincrement=True, comment='id 自增')

    # pro_id  = Column(key='pro_id', type_=Integer(), nullable=False,  comment='项目方id')
    pro_id = Column(Integer(), ForeignKey(Project.pro_id), comment='项目方ID')
    project = relationship("Project", backref='ref_deposit_project')


    token_name = Column(key='token_name', type_=  String(20), nullable=False ,  comment='币种' )
    tx_hash = Column(key='tx_hash', type_=String(100), nullable=False,  comment='交易hash(txid)')

    from_addr = Column(key='from_addr', type_=String(100), nullable=False, comment='源地址', )
    to_addr = Column(key='to_addr', type_=String(100), nullable=False, comment='目的地址')
    memo = Column(key='memo', type_=String(100), nullable=True, comment='转账备注(memo), 有些币种需要带memo, 例如 EOS, XRP')
    amount = Column(key='amount', type_=DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='充币金额')
    block_height = Column(key='block_height', type_= BigInteger(),   nullable=False, index=True, comment='交易所在区块高度' )
    block_time = Column(key='block_time', type_=DateTime(timezone=True), nullable=False, index=True, comment='区块时间戳')
    notify_status = Column(key='notify_status', type_=Integer(), default=0, nullable=False,
                           comment='通知状态, 0:未通知, 1: 通知成功 , 2:通知失败')
    tx_confirmations = Column(key='tx_confirmations', type_=Integer(), nullable=False, comment='交易的区块确认数')

    __table_args__ = (
        UniqueConstraint( 'pro_id','token_name','tx_hash', 'to_addr', name='uidx_pro_id_token_name_tx_hash_to_addr'),  # 联合唯一索引
        Index('idx_for_query_by_block_height',   'pro_id' , 'token_name',  'block_height' ),  #设置联合索引, 为了根据区块高度查询
        Index('idx_for_query_by_block_time',   'pro_id' , 'token_name',  'block_time' ), #设置联合索引, 为了根据区块时间查询
    )


    def __repr__(self):

        #TODO:打印其他的字段
        return  f"Deposit(pro_id:{self.pro_id}, token_name:'{self.token_name}"\
                f"tx_hash:{self.tx_hash}', from_addr:{self.from_addr}, to_addr:{self.to_addr}"\
                 f"amount:{self.amount})"
    pass



class ActiveAddressBalance(ORMBase):
    """
    活跃地址的余额表, 用来归集
    """

    __tablename__ = 'tb_active_address_balances'

    token_name = Column(key='token_name', type_=  String(20), nullable=False , primary_key=True, comment='币种' )
    address = Column(key='address', type_=String(100), nullable=False, primary_key=True, comment='地址' )
    # pro_id  = Column(key='pro_id', type_=Integer(), nullable=False,  comment='项目方id')
    balance = Column(key='balance', type_=DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='充币金额')
    update_time = Column(key='update_time', type_=DateTime(timezone=True), nullable=False, primary_key=False, comment='最后更新时间')

    pro_id = Column(Integer(), ForeignKey(Project.pro_id), comment='项目方ID')
    project = relationship("Project", backref='ref_active_addr_project')


    def __repr__(self):

        return  f"ActiveAddressBalance(pro_id:{self.pro_id}, token_name:'{self.token_name}"\
                f" , address:{self.address}', balance:{self.balance})"

    pass


class  ScanStartBlock(ORMBase):
    """
    记录区块扫描的高度
    """
    __tablename__ = 'tb_scan_start_height'

    token_name = Column(key='token_name', type_=String(20), nullable=False, primary_key=True, comment='币种, 统一使用大写!')
    block_height = Column(key='block_height', type_=Integer(), default=0, nullable=False, comment='区块高度')

    def __repr__(self):
        return f"ScannStartBlock(token_name:{self.token_name}, tx_hash:{self.block_height})"


class Address(ORMBase):
    """
    充币地址表
    """

    __tablename__ = 'tb_address'

    address = Column(key='address', type_=String(100), primary_key=True, nullable=False, comment='地址' )
    token_name =Column(key='token_name', type_= String(20),  nullable=False ,  comment='币种名')
    account_index =   Column(key='account_index', type_=Integer(), nullable=False, comment='账户索引')
    address_index =   Column(key='address_index', type_=Integer(), nullable=False, comment='地址索引')
    create_time = Column(key='create_time', type_=DateTime(timezone=True), default=datetime.datetime.now(),  nullable=False, comment='添加的时间')

    # pro_id = Column(key='pro_id', type_=Integer(), nullable=False, comment='项目方id')

    pro_id = Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='address_ref_project')

    def __repr__(self):
        return f"Address(address={self.address}, token_name={self.token_name}, pro_id={self.pro_id}, " \
               f"account_index={self.account_index}, address_index={self.address_index}, create_time={self.create_time}"
        pass
