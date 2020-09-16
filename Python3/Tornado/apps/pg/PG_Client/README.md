# PG_Client 

支付网关 客户端管理台服务

# 环境

- Linux/Windows/MacOS 
- 开发框架: djangorestframework
- 官方文档: https://www.django-rest-framework.org/
- 快速上手: https://www.django-rest-framework.org/tutorial/quickstart/


# 依赖安装

```

pip install django
pip install djangorestframework

```


# 功能开发

- 用户登录/密码修改等
- 数据的查询/修改
- API鉴权/限频

# 支付网关2.0 PG_Admin model新增

Project model 新增字段

1. password 密码	
    - 类型: varchar
    - 长度: 200 
    - 不为空
    	
2. last_login 上次登录 
    - 类型: datetime 
    - 长度: 6
    - 可以为空

# 支付网关2.0 新增 model

1. Address
    名称(地址管理)

    字段
    - id(主键)
    - token_name(varchar, 长度:20, 不为空)
    - address_nums(int, 不为空, 默认为0)
    - uncharged_address_nums(int, 不为空, 默认为0)
    - update_time(datetime, 不为空, 根据服务器时间)
    - pro_id(外键)
    - 联合唯一索引("token_name", "pro_id")
    - 表名 tb_address_admin

2. UserAddressBalances
    名称(用户地址资产) (支付网关1.0时表已经存在)
    
    字段
    - pro_id(外键)
    - token_name(varchar, 长度:20, 不为空)
    - address(varchar, 长度:100, 不为空)
    - balance(Decimal,长度:28, 小数位:8, 不为空)
    - update_time(datetime, 不为空)
    - 联合唯一索引("token_name", "address")
    - 表名 tb_active_address_balances
   
3. UserTokenBalances
    名称(用户币种资产)
    
    字段
    - id(主键)
    - pro_id(外键)
    - token_name(varchar, 长度:20, 不为空)
    - all_balance(Decimal,长度:28, 小数位:8, 不为空)
    - withdraw_address(varchar, 长度:100, 不为空)
    - withdraw_balance(Decimal,长度:28, 小数位:8, 不为空)
    - update_time(datetime, 不为空)
    - 联合唯一索引("pro_id", "token_name")
    - 表名 tb_user_token_balances
  
4. AssetDailyReport
    名称(资产日报表)
    
    字段
    - pro_id(外键)
    - token_name(varchar, 长度:20, 不为空)
    - deposit_amount(Decimal,长度:28, 小数位:8, 不为空)
    - withdraw_amount(Decimal,长度:28, 小数位:8, 不为空)
    - collectionRecords_amount(Decimal,长度:28, 小数位:8, 不为空)
    - all_balance(Decimal,长度:28, 小数位:8, 不为空)
    - update_time(datetime, 不为空)
    - 表名 tb_asset_daily_report
   
5. UserOperationLog
    名称(用户操作日志)
    
    字段
    - id(主键)
    - pro_id(外键)
    - operation_time(datetime, 不为空)
    - function_name(varchar, 长度:50, 不为空)
    - operation_type(varchar, 长度:20, 不为空)
    - update_before_value(varchar, 长度:100, 不为空, 默认为空)
    - last_after_value(varchar, 长度:100, 不为空, 默认为空)
    - operation_status(varchar, 长度:20, 不为空)
    - 表名 tb_user_operation_log
    
# 支付网关2.0 安装包统一用外部总requirements.txt