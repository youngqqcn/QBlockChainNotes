#!coding:utf8

#author:yqq
#date:2020/5/8 0008 16:31
#description:


#!coding:utf8

#author:yqq
#date:2020/4/30 0030 19:06
#description:    这里写  ORM的  model


# 数据库操作使用 ORM
# https://www.cnblogs.com/liu-yao/p/5342656.html
# 中文文档:  https://www.osgeo.cn/sqlalchemy/
#可以参考: https://blog.csdn.net/qq_36019490/article/details/96883453
import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, BOOLEAN
from sqlalchemy import UniqueConstraint, Index, DECIMAL, TIMESTAMP , create_engine, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,  backref, relationship

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
        return f"Address(address={self.address}, token_name={self.token_name}, pro_id={self.pro_id}, "\
                f"account_index={self.account_index}, address_index={self.address_index}, create_time={self.create_time}"



class AddAddressOrder(ORMBase):
    """
    地址申请订单表
    """


    __tablename__ = 'tb_add_address_order'


    order_id = Column(key='order_id', type_=String(30), primary_key=True,  nullable=False, comment='order_id')
    # pro_id = Column(key='pro_id', type_=Integer(), nullable=False, comment='项目方id')
    token_name = Column(key='token_name', type_=String(20),  nullable=False, comment='币种名')
    apply_times = Column(key='apply_times', type_=Integer(), nullable=False, comment='本次是第几次申请')
    count =  Column(key='count', type_=Integer(), nullable=False, comment='申请数量')
    start_addr_index = Column(key='start_addr_index', type_=Integer(), nullable=False, comment='本次生成,起始地址索引')
    end_addr_index = Column(key='end_addr_index', type_=Integer(), nullable=False, comment='本次生成,结束地址索引')
    audit_status = Column(key='audit_status', type_= String(20),  nullable=False, comment='审核状态, PENDING:待审核, REJECTED:已拒绝, PASSED:已通过')
    generate_status = Column(key='generate_status', type_= String(20),  nullable=False, comment='地址生成状态, NOTYET:未生成, SUCCESS:生成完成')
    order_create_time = Column(key='order_create_time', type_=DateTime(timezone=True),  nullable=False, comment='订单生成时间')
    audit_complete_time =  Column(key='audit_complete_time', type_=DateTime(timezone=True),   nullable=True, comment='订单审核完成(通过或拒绝)时间')
    order_complete_time =  Column(key='order_complete_time', type_=DateTime(timezone=True),  nullable=True, comment='订单完成时间')
    order_status = Column(key='order_status', type_= String(20),  nullable=False, comment='订单状态, PROCESSING:处理中, SUCCESS:成功, FAIL:失败')
    remark = Column(key='remark', type_= String(250),  nullable=True, comment='备注')

    active_status = Column(key='active_status', type_= String(10), nullable=False , comment='启用状态, NO:未启用, YES:已启用')

    pro_id = Column(Integer(), ForeignKey(Project.pro_id, ondelete='CASCADE'), comment='项目方ID')
    project = relationship("Project", backref='add_address_ref_project')


    def __repr__(self):
        return 'AddAddressOrder'




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



