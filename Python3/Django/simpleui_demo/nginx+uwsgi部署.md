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

  

- 启动 uwsgi  :  `uwsgi --ini ./uwsgi.ini`
  

### nginx配置

- nginx 配置 

  ```conf
  
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

  

- 测试配置文件语法: `nginx -t  -c  配置文件的绝对路径` 
- 启动 nginx :  `nginx -c 配置文件的绝对路径`
- 重新加载配置文件  :  `nginx -s reload`
- 退出nginx : `nginx -s quit`





### 使用supervisor监控uwsgi进程

- TODO : 未解决虚拟环境的问题 







## 效果

<http://114.55.93.92:50392/admin/>