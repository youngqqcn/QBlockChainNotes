@echo off
echo setting PG env........

set regpath=HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment


set env_name_k=ENV_NAME
set env_name_v=sit
reg add "%regpath%" /v %env_name_k% /d %env_name_v% /f

set mnemonic_k=MNEMONIC
set mnemonic_v=D:\my_words.dat
reg add "%regpath%" /v %mnemonic_k% /d %mnemonic_v% /f



set rabbit_mq_host_k=RABBIT_MQ_HOST
set rabbit_mq_host_v="192.168.10.29"
reg add "%regpath%" /v %rabbit_mq_host_k% /d %rabbit_mq_host_v% /f

set rabbit_mq_port_k=RABBIT_MQ_PORT
set rabbit_mq_port_v=5672
reg add "%regpath%" /v %rabbit_mq_port_k% /d %rabbit_mq_port_v% /f


set rabbit_mq_user_name_k=RABBIT_MQ_USER_NAME
set rabbit_mq_user_name_v=admin
reg add "%regpath%" /v %rabbit_mq_user_name_k% /d %rabbit_mq_user_name_v% /f


set rabbit_mq_password_k=RABBIT_MQ_PASSWORD
set rabbit_mq_password_v="123456"
reg add "%regpath%" /v %rabbit_mq_password_k% /d %rabbit_mq_password_v% /f


set eth_full_node_host_k=ETH_FULL_NODE_HOST
set eth_full_node_host_v="192.168.10.199"
reg add "%regpath%" /v %eth_full_node_host_k% /d %eth_full_node_host_v% /f

set eth_full_node_port_k=ETH_FULL_NODE_PORT
set eth_full_node_port_v=28545
reg add "%regpath%" /v %eth_full_node_port_k% /d %eth_full_node_port_v% /f


set htdf_node_host_k=HTDF_NODE_HOST
set htdf_node_host_v="htdf2020-test01.orientwalt.cn"
reg add "%regpath%" /v %htdf_node_host_k% /d %htdf_node_host_v% /f


set htdf_node_port_k=HTDF_NODE_PORT
set htdf_node_port_v=1317
reg add "%regpath%" /v %htdf_node_port_k% /d %htdf_node_port_v% /f


set btc_api_host_k=BTC_API_HOST
set btc_api_host_v="192.168.10.199"
reg add "%regpath%" /v %btc_api_host_k% /d %btc_api_host_v% /f


set btc_api_port_k=BTC_API_PORT
set btc_api_port_v=3001
reg add "%regpath%" /v %btc_api_port_k% /d %btc_api_port_v% /f



set mysql_host_k=MYSQL_HOST
set mysql_host_v="192.168.10.29"
reg add "%regpath%" /v %mysql_host_k% /d %mysql_host_v% /f

set mysql_port_k=MYSQL_PORT
set mysql_port_v=3306
reg add "%regpath%" /v %mysql_port_k% /d %mysql_port_v% /f

set mysql_username_k=MYSQL_USERNAME
set mysql_username_v=root
reg add "%regpath%" /v %mysql_username_k% /d %mysql_username_v% /f

set mysql_pwd_k=MYSQL_PWD
set mysql_pwd_v="eWFuZ3FpbmdxaW5n"
reg add "%regpath%" /v %mysql_pwd_k% /d %mysql_pwd_v% /f

set redis_host_k=REDIS_HOST
set redis_host_v="192.168.10.29"
reg add "%regpath%" /v %redis_host_k% /d %redis_host_v% /f

set redis_port_k=REDIS_PORT
set redis_port_v=6379
reg add "%regpath%" /v %redis_port_k% /d %redis_port_v% /f

set redis_user_k=REDIS_USER
set redis_user_v=root
reg add "%regpath%" /v %redis_user_k% /d %redis_user_v% /f

set redis_password_k=REDIS_PASSWORD
set redis_password_v="123456"
reg add "%regpath%" /v %redis_password_k% /d %redis_password_v% /f


set sms_api_url_k=SMS_API_URL
set sms_api_url_v="---TODO----"
reg add "%regpath%" /v %sms_api_url_k% /d %sms_api_url_v% /f

set sms_sn_k=SMS_SN
set sms_sn_v="---TODO----"
reg add "%regpath%" /v %sms_sn_k% /d %sms_sn_v% /f

set sms_pwd_k=SMS_PWD
set sms_pwd_v="---TODO------"
reg add "%regpath%" /v %sms_pwd_k% /d %sms_pwd_v% /f


echo successed.
pause
