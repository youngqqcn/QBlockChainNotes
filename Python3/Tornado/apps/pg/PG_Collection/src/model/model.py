#!coding:utf8

#author:yqq
#date:2020/5/19 0019 11:06
#description:


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


class ActiveAddressBalance(ORMBase):
    """
    活跃地址的余额表, 用来归集
    """

    __tablename__ = 'tb_active_address_balances'

    token_name = Column(key='token_name', type_=  String(20), nullable=False , primary_key=True, comment='币种' )
    address = Column(key='address', type_=String(100), nullable=False, primary_key=True, comment='地址' )
    pro_id  = Column(key='pro_id', type_=Integer(), nullable=False,  comment='项目方id')
    balance = Column(key='balance', type_=DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='充币金额')
    update_time = Column(key='update_time', type_=DateTime(timezone=True), nullable=False, primary_key=False, comment='最后更新时间')


    def __repr__(self):

        return  f"ActiveAddressBalance(pro_id:{self.pro_id}, token_name:'{self.token_name}"\
                f" , address:{self.address}', balance:{self.balance})"

    pass




class CollectionConfig(ORMBase):
    """
    归集配置表
    """

    __tablename__ = 'tb_collection_config'


    id = Column(key='id', type_=Integer(), primary_key=True, autoincrement=True, comment='id 自增')
    token_name = Column(key='token_name', type_=String(20), nullable=False, comment='币种名')
    collection_dst_addr = Column(key='address', type_=String(100), nullable=False, comment='出币地址')
    min_amount_to_collect = Column(key='min_amount_to_collect',
                        type_=DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True),
                        nullable=False, comment='最小归集金额')

    pro_id = Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='collection_config_ref_project')

    __table_args__ = (
        UniqueConstraint('token_name', 'pro_id', name='uidx_token_name_pro_id'),  # 联合唯一索引
    )

    def __repr__(self):
        return f'CollectionConfig(pro_id:{self.pro_id}, token_name:{self.token_name}, ' \
               f'collection_dst_addr:{self.collection_dst_addr}, min_amount_to_collect:{self.min_amount_to_collect} )'




class CollectionFeeConfig(ORMBase):
    """
    归集  手续费地址配置
    """

    __tablename__ = 'tb_collection_fee_config'


    id = Column(key='id', type_=Integer(), primary_key=True, autoincrement=True, comment='id 自增')
    token_name = Column(key='token_name', type_=String(20), nullable=False, comment='币种名')
    address = Column(key='address', type_=String(100), nullable=False, comment='出币地址')
    pro_id = Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='collection_fee_config_ref_project')

    __table_args__ = (
        UniqueConstraint('token_name', 'pro_id', name='uidx_token_name_pro_id'),  # 联合唯一索引
    )



class  CollectionRecords(ORMBase):
    """
    归集记录
    """

    __tablename__ = 'tb_collection_records'


    id = Column(key='id', type_=Integer(), primary_key=True, autoincrement=True, comment='id 自增')
    token_name = Column(key='token_name', type_=String(20), nullable=False, comment='币种名')
    from_address = Column(key='from_address', type_=String(100), nullable=False, comment='源地址')
    to_address = Column(key='to_address', type_=String(100), nullable=False, comment='目的地址')
    amount = Column(key='amount', type_=DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True),
                                   nullable=False, comment='归集金额')
    complete_time = Column(key='complete_time', type_=DateTime(timezone=True), nullable=True, comment='完成时间')

    block_height = Column(key='block_height', type_=BigInteger(), default=0, nullable=False, comment='交易所在区块高度')
    block_time = Column(key='block_time', type_=DateTime(timezone=True), nullable=True, comment='区块时间戳')
    transaction_status = Column(key='transaction_status', type_=String(20), nullable=False,
                                comment='交易状态, NOTYET:尚未汇出, PENDING:已转出,等待交易为被打包进区块, FAIL :交易失败, SUCCESS : 交易成功 ')

    collection_type = Column(key='collection_type', type_=String(20), nullable=False, comment="归集类型")

    tx_hash = Column(key='tx_hash', type_=String(100), nullable=False, comment='交易hash(txid)')

    pro_id = Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='collection_records_ref_project')
    tx_confirmations = Column(key='tx_confirmations', type_=Integer(), nullable=False, default=0 ,comment='交易的区块确认数')

    def __repr__(self):
        return f'CollectionRecords(id:{self.id}, token_name:{self.token_name}, from_address:{self.from_address}, ' \
               f'to_address:{self.to_address}, amount:{self.amount}, tx_hash:{self.tx_hash} )'




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