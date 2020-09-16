#!coding:utf8

#author:yqq
#date:2020/4/30 0030 19:06
#description:    这里写  ORM的  model


# 数据库操作使用 ORM
# https://www.cnblogs.com/liu-yao/p/5342656.html
# 中文文档:  https://www.osgeo.cn/sqlalchemy/
#可以参考: https://blog.csdn.net/qq_36019490/article/details/96883453

from sqlalchemy import Column, Integer, String, \
    Text, ForeignKey, DateTime, UniqueConstraint, Index, DECIMAL, \
    create_engine, BigInteger, BOOLEAN

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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



class WithdrawConfig(ORMBase):
    """
    提币配置表
    """


    __tablename__ = 'tb_withdraw_config'


    #关于外键:
    #   https://blog.csdn.net/lucyxu107/article/details/81743529
    #  https://www.cnblogs.com/chen1930/p/6224676.html

    # pro_id = Column(key='pro_id', type_=Integer(), nullable=False, comment='项目方id')
    id = Column( key='id', type_=Integer(), primary_key=True, autoincrement=True , comment='id 自增')
    token_name = Column(key='token_name', type_=String(20),  nullable=False, comment='币种名')
    address = Column(key='address', type_=String(100),  nullable=False, comment='出币地址' )
    min_amount = Column( key='min_amount', type_= DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='最大提币金额'  )
    max_amount = Column( key='max_amount', type_= DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='最小提币金额'  )
    balance_threshold_to_sms = Column( key='balance_threshold_to_sms', type_= DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='短信通知阈值'  )
    is_open  =   Column( key='is_open', type_=BOOLEAN(), nullable=True, comment='提币通过是否开启' )

    # pro_id =  Column(Integer(), ForeignKey('tb_project.pro_id'))
    pro_id =  Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='withdraw_config_ref_project')

    __table_args__ = (
        UniqueConstraint('token_name', 'pro_id', name='uidx_token_name_pro_id'),  #联合唯一索引
    )




class WithdrawOrder(ORMBase):
    __tablename__ = 'tb_withdraw_order'

    serial_id = Column(key='serial_id', type_=String(30), primary_key=True, comment='支付网关系统自己生成的流水id')
    order_id = Column(key='order_id', type_= String(30), index=True,  nullable=False,  comment='用户传来的order_id')
    # pro_id = Column(key='pro_id', type_=Integer(), nullable=False, index=False, comment='项目方id')

    pro_id = Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='withdraw_order_ref_project')

    token_name =Column(key='token_name', type_= String(20), nullable=False, comment='币种名')
    from_addr = Column(key='from_addr', type_=  String(100), nullable=False , comment='源地址', )
    to_addr = Column(key='to_addr' , type_= String(100), nullable=False, comment='目的地址' )
    memo = Column(key='memo', type_=String(100), nullable=True, comment='转账备注(memo), 有些币种需要带memo, 例如 EOS, XRP')
    amount = Column( key='amount', type_= DECIMAL(precision=28, scale=8, decimal_return_scale=8, asdecimal=True), nullable=False, comment='金额'  )
    block_height = Column(key='block_height', type_= BigInteger(),  default=0 , nullable=False, comment='交易所在区块高度' )
    tx_hash = Column(key='tx_hash' , type_= String(100), nullable=False, comment='交易hash(txid)' )
    callback_url = Column(key='callback_url', type_=String(250), nullable=False, comment='回调通知接口url')
    tx_confirmations = Column(key='tx_confirmations', type_=Integer(), nullable=False, comment='交易的区块确认数')

    order_status = Column(key='order_status', type_= String(20),  nullable=False, comment='订单状态, PROCESSING:处理中, SUCCESS:已成功, FAIL:已失败')

    transaction_status = Column(key='transaction_status', type_= String(20),   nullable=False,
                                comment='交易状态, NOTYET:尚未汇出, PENDING:已转出,等待交易为被打包进区块, FAIL :交易失败, SUCCESS : 交易成功 ' )

    notify_status =  Column(key='notify_status', type_= String(20),  nullable=False,
                            comment='通知状态, NOTYET:尚未通知, FIRSTSUCCESS:"已汇出"通知成功, FIRSTFAIL:"已汇出"通知失败, SECONDSUCCESS:第二次通知成功, SECONDFAIL:第二次通知失败' )
    notify_times = Column(key='notify_try_times', type_= Integer(),  default=0 , nullable=False, comment='通知次数, 记录通知的次数(包括成功和失败)' )
    block_time = Column(key='block_time', type_=DateTime(timezone=True), nullable=True, comment='区块时间戳')
    complete_time = Column(key='complete_time', type_=DateTime(timezone=True), nullable=True, comment='订单完成时间')
    remark = Column(key='remark' , type_= String(250), nullable=True , comment='订单说明,保存一些说明信息' )





    def __repr__(self):
        #TODO: 将其他字段也打印出来
        return  f"WithdrawOrder(serial_id={self.serial_id}, order_id={self.order_id}, pro_id={self.pro_id}...)"











