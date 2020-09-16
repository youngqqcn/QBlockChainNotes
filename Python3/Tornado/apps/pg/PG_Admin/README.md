# PG_Admin

Payment  Gateway Admin

支付网关管理台


### 安装依赖 


```shell

yum install mysql-devel



```



### 创建超级管理员

```
python manage.py createsuperuser
```

### 静态资源部署

```
python manage.py collectstatic

```



### nginx 安装

```shell

cd ~/downloads

wget http://nginx.org/download/nginx-1.18.0.tar.gz

tar xzvf nginx-1.18.0.tar.gz

./configure --prefix=/usr/local/nginx


ln -s /usr/local/nginx/sbin/nginx  /usr/bin/nginx




```


### 反向代理+ runserver

```shell

#测试配置文件
nginx -t -c /data/PaymentGateway/PG_Admin/nginx_admin.conf


#启动
nginx  -c /data/PaymentGateway/PG_Admin/nginx_admin.conf

```




### uwsgi 配置

- `pip installl uwsgi`

- 编辑`uwsgi.ini`

  ```
  [uwsgi]
  #使用nginx是使用
  
  #使用socket端口, 需要先启动uwsgi,在启动nginx, 否则可能出现端口占用的情况,导致uwsgi无法启动
  #socket=0.0.0.0:9000
  
  #使用socket文件
  socket=/data/py3/simpleui_demo/socket.sock
  
  #如果使用 http反向代理, 即nginx使用prox_pass
  #http=0.0.0.0:9000
  
  virtualenv=/data/py3/venv/
  chdir = /data/py3/simpleui_demo 
  wsgi-file = simpleui_demo/wsgi.py
   
  processes = 1
  threads = 1
   
  #chmod-socket = 664
  enable-threads=True
  master=True
  pidfile=uwsgi.pid
  daemonize=uwsgi.log
  ```

- 启动 uwsgi : `uwsgi --ini ./uwsgi.ini`

### nginx配置

- nginx 配置

  ```
  worker_processes  1;
  
  events {
  #use epoll;
      worker_connections  1024;
  }
  
  
  http {
      include       /usr/local/nginx/conf/mime.types;
      default_type  application/octet-stream;
  
  
      sendfile        on;
  
      keepalive_timeout  65;
  
      #gzip  on;
  
      server {
          listen       50392;
          server_name _;
  
          #charset koi8-r;
          charset utf-8;
          root /data/py3/simpleui_demo;
  
          location / {
              include       /usr/local/nginx/conf/uwsgi_params;
  #uwsgi_pass 127.0.0.1:9000;
              uwsgi_pass unix:///data/py3/simpleui_demo/socket.sock;
          }
  
          location /static/ {
              alias /data/py3/simpleui_demo/static/;
          }
  
          location /media/ {
              alias /data/py3/simpleui_demo/media/;
          }
  
          error_page  404              /404.html;
          error_page   500 502 503 504  /50x.html;
          location = /50x.html {
              root   html;
          }
  
          
      }
  
  }
  ```

- 测试配置文件语法: `nginx -t -c 配置文件的绝对路径`

- 启动 nginx : `nginx -c 配置文件的绝对路径`

- 重新加载配置文件 : `nginx -s reload`

- 退出nginx : `nginx -s quit`

### 使用supervisor监控uwsgi进程

- TODO : 未解决虚拟环境的问题

## 效果

http://114.55.93.92:50392/admin/




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
    
# 支付网关2.0 生产环境需要改 
    - PG_Admin 中的settings.py 修改
    - ERC20_USDT_CONTRACT_ADDRESS为主网USDT
   
# 支付网关2.0 新增运行脚本
    Makefile中 make start会自动开启
    文件路径: PG_Admin/pgadmin/signals.py
    功能为: 自动查询地址管理,币总资产,日资产
     

# 支付网关2.0 安装包统一用外部总requirements.txt


# 支付网关3.0 新增model

1. GoogleCode

    - id(主键)
    - pro_id(外键)
    - key (varchar, 长度: 50, 不为空)
    - logined(int, 是否已登录过, 项目方标识, 可以为空)
    - is_superuser(int, 是否是管理员, 可以为空)
    - 表名 tb_google_code
   
2. DjangoAdminLog
    
    套用Django log 表 未新增

# 支付网关3.0 查询脚本新增
    谷歌验证码初始化




























