# PG_Withdraw

- Payment Gateway Withdraw

- 支付网关提币



## 服务器部署步骤

- 在 `~/.bashrc` 中添加 

```shell
export PYTHONPATH=/data/PaymentGateway/PG_Withdraw/:$PYTHONPATH
```


- 创建虚拟环境

```shell

cd /

mkdir data

mkdir PaymentGateway

cp -R  PG_Withdraw  /data/PaymentGateway

python3 -m venv venv

source /data/PaymentGateway/venv  

cd PG_Withdraw

#如果安装太慢, 修改pip软件源为豆瓣即可
pip install -r requirements.txt   

make  start-testnet  或  make start-mainnet

```



- 环境变量


Linux:
```shell
export ENV_NAME='sit'
export MNEMONIC=''
export RABBIT_MQ_HOST=''
export RABBIT_MQ_PORT=1234
export RABBIT_MQ_USER_NAME=''
export RABBIT_MQ_PASSWORD=''
export ETH_FULL_NODE_HOST=''
export ETH_FULL_NODE_PORT=1234
export HTDF_NODE_HOST=''
export HTDF_NODE_PORT=1234
export MYSQL_HOST=''
export MYSQL_PORT=1234
export MYSQL_USERNAME=''
export MYSQL_PWD=''
export REDIS_HOST=''
export REDIS_PORT=1234
export REDIS_USER=''
export REDIS_PASSWORD=''
export SMS_API_URL=''
export SMS_SN=''
export SMS_PWD=''
```



Windows

```bat
::添加支付网关环境变量
@echo off
echo 设置支付网关环境变量
set regpath=HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment


set env_name_k=ENV_NAME
set env_name_v=sit
reg add "%regpath%" /v %env_name_k% /d %env_name_v% /f

set mnemonic_k=MNEMONIC
set mnemonic_v=xxxxx
reg add "%regpath%" /v %mnemonic_k% /d %mnemonic_v% /f


set rabbit_mq_host_k=RABBIT_MQ_HOST
set rabbit_mq_host_v=xxx
reg add "%regpath%" /v %rabbit_mq_host_k% /d %rabbit_mq_host_v% /f

set rabbit_mq_port_k=RABBIT_MQ_PORT
set rabbit_mq_port_v=xxxx
reg add "%regpath%" /v %rabbit_mq_port_k% /d %rabbit_mq_port_v% /f


set rabbit_mq_user_name_k=RABBIT_MQ_USER_NAME
set rabbit_mq_user_name_v=xxxx
reg add "%regpath%" /v %rabbit_mq_port_k% /d %rabbit_mq_port_v% /f


set rabbit_mq_password_k=RABBIT_MQ_PASSWORD
set rabbit_mq_password_v=xxxx
reg add "%regpath%" /v %rabbit_mq_port_k% /d %rabbit_mq_port_v% /f


set eth_full_node_host_k=ETH_FULL_NODE_HOST
set eth_full_node_host_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f


set htdf_node_host_k=HTDF_NODE_HOST
set htdf_node_host_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f


set htdf_node_port_k=HTDF_NODE_PORT
set htdf_node_port_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set mysql_host_k=MYSQL_HOST
set mysql_host_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set mysql_port_k=MYSQL_PORT
set mysql_port_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set mysql_username_k=MYSQL_USERNAME
set mysql_username_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set mysql_pwd_k=MYSQL_PWD
set mysql_pwd_v=xxxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set redis_host_k=REDIS_HOST
set redis_host_v=xxxx
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set redis_port_k=REDIS_PORT
set redis_port_v=xxxy
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set redis_user_k=REDIS_USER
set redis_user_v=xxxy
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set redis_password_k=REDIS_PASSWORD
set redis_password_v=xxxy
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f


set sms_api_url_k=SMS_API_URL
set sms_api_url_v=xxxxxx
reg add "%regpath%" /v %sms_api_url_k% /d %sms_api_url_v% /f

set sms_sn_k=SMS_SN
set sms_sn_v=xxxxxxxxxx
reg add "%regpath%" /v %sms_sn_k% /d %sms_sn_v% /f

set sms_pwd_k=SMS_PWD
set sms_pwd_v=xxxxxxxxxxxxxxx
reg add "%regpath%" /v %sms_pwd_k% /d %sms_pwd_v% /f


pause
```












