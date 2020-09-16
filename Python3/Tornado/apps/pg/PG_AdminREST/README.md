## PG_AdminREST

沙暴管理台后端 RESTful 接口


# 停止
make stop

# 启动 
make start

# 环境

source /data/PaymentGateway/venv/bin/activate

# 测试启动

python3 manage.py runserver 

# 版本 1.0

功能如下:
     细节在views文件下
     
    'UsersViewSet', 
    'WithdrawOrderViewSet', 
    'DepositViewSet',
    'CollectionRecordsViewSet', 
    'AddressViewSet', 
    'SubaddressViewSet',
    'CollectionConfigViewSet'
    'WithdrawConfigViewSet',
    'CollectionFeeConfigViewSet',
    'UserAddressBalancesViewSet',
    'UserTokenBalancesViewSet',
    'AssetDailyReportViewSet',
    'UserOperationLogViewSet',
    'AddAddressOrderViewSet',
    'Reset', 
    'ResetKey',
    'ResetGoogleCode',
    'ObtainJSONWebToken',
    'RefreshJSONWebToken', 
    'AdminReset',
    'AdminOperationLogViewSet'


