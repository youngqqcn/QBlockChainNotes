# Docker学习笔记


### Docker的基本组成

- Docker客户端 /守护进程
C/S架构
本地/远程

- Docker镜像


- Docker容器

- Docker Registry  仓库
 公有
 私有
 Docker Hub

### Docker优点

Docker容器的能力
- 文件系统隔离:每个容器都有自己的root文件系统
- 进程隔离:每个容器都运行在自己的进程环境中
- 网络隔离:容器间的虚拟网络接口和IP地址都是分开的
- 资源隔离和分组:使用 groups将CPU和内存之类的资源独立分配给每个
Docker容器


 ### Docker安装和配置

 #### Ubuntu安装

```
uname -a   //查看linux内核
```

### 添加用户组
```
sudo groupadd docker
sudo gpasswd -a ${USER} docker
sudo service docker restart
newgrp - docker
重新登录即可, 就不用使用sudo了
```




### 容器的基本操作

#### 启动容器

```
docker run IMAGE [COMMAND][ARG...]
例如:
docker run ubuntu echo "hello docker"  //如果本地没有Ubuntu镜像, 会从docker hub中拉取
```

#### 启动交互式容器

```
docker run -i -t IMAGE  /bin/bash
-i        --interactive=true|fase   默认是false
-t      --tty=true|false 默认是false
例如:

```


#### 查看docker容器

```
docker  -ps   //查看正在运行的容器
docker -ps -a //查看所有容器
docker inspect   容器id或者容器名字    //查看容器信息

```


#### 重新启动停止的容器

```
docker start -i   
```

#### 删除已经停止的容器

```
docker rm  容器id
```




#### 守护式容器

- 方法一
```
docker run -i -t IMAGE  /bin/bash       //使用  ctrl+p 和 ctrl+q 退出交互式容器
docker attach  容器id      //重新进入, 守护式容器
```

- 方法二
```
docker run -d ubuntu /bin/bash     //以守护进程方式运行命令, 命令运行完了,就退出了
```



#### 查看容器日志

```
docker logs [-f][-t][--tail]  容器名  

例如:
  docker logs -tf  --tail 0 66002527b240
```


#### 查看运行中的容器内部进程情况

```
docker top  容器id
```

#### 在运行中的容器内启动新进程

```
docker exce [-d][-i][-t]  容器id或者容器名字  [COMMAND][ARG...]

例如:

 docker exec -i -t 66002527b240 /bin/bash
 然后退出
 用docker top 查看即可
```


#### 停止运行容器

```
docker stop   //发送结束信号, 等待容器运行结束, 并返回容器id
docker kill   //直接杀死, 并返回容器id
```



#### Docker帮助文档

```
man docker-run
man docker-logs
...
```


### Docker镜像操作

#### 查看docker镜像

```
docker images
docker images --no-trunk
```



#### 查看image的详细信息
```
docker inspect  imageID

```


#### 删除镜像

```
docker rmi  imageID .....
```



```
docker search [OPTION] TERM
--automated
-s  制定star的数量
```



#### 拉取镜像
```
docker pull
```

#### 推送镜像
```
docker push
```


### 构建镜像(重点掌握)

- docker commit 通过容器构建

```
docker commit [OPTION] CONSTAINER [REPOSITORY[:TAG]]
- a, author=""   
-m, --message=""  
-p, --pause=true   Pause contanier during commit
```

例如:
```
docker ps -a   //查看所有容器, 找到修改过的容器对应的id
docker commit -a "yqq" -m "ubuntu-with-vim" ca06b5a473ae ubuntu_with_vim  //创建镜像

```

实际例子, 在Ubuntu镜像中安装了一些软件, 作为以后自己的开发环境
```
root@88063c36274a:/mine/go# exit   //退出容器
exit
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$ docker ps -a  //查看所有容器
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                     PORTS                  NAMES
88063c36274a        aliyun_ubuntu       "/bin/bash"              20 minutes ago      Exited (0) 8 seconds ago                          trusting_edison
56bbd50e13b5        nginx               "nginx -g 'daemon of…"   2 hours ago         Up 2 hours                 0.0.0.0:8080->80/tcp   epic_wing
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$ docker commit -a "yqq" -m "installed golang python g++" 88063c36274a my_dev_ubuntu      //提交刚才修改过的容器, 生成镜像   
sha256:58978f24808959effa333e86a0c9163b7c1bd1c98f74dd5fb5c6d004408b35c8
yqq@ubuntu18-04:~$ docker images   //查看所有镜像
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
my_dev_ubuntu       latest              58978f248089        6 seconds ago       688MB
aliyun_ubuntu       latest              05a713fa81c4        23 minutes ago      204MB
ubuntu_test_test    latest              d27f050e1bc0        About an hour ago   86.2MB
nginx               latest              568c4670fa80        12 days ago         109MB
ubuntu              18.04               93fd78260bd1        2 weeks ago         86.2MB
ubuntu              latest              93fd78260bd1        2 weeks ago         86.2MB
centos              centos7.1.1503      000733bc1a76        2 months ago        212MB
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$
yqq@ubuntu18-04:~$ docker run -i -t my_dev_ubuntu /bin/bash    //运行刚才的镜像
root@bab9fb62deb4:/# g++    //安装了g++
g++: fatal error: no input files
compilation terminated.
root@bab9fb62deb4:/# gcc  //安装了gcc
gcc: fatal error: no input files
compilation terminated.
root@bab9fb62deb4:/# python    //安装了python
Python 2.7.15rc1 (default, Nov 12 2018, 14:31:15)
[GCC 7.3.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>>

```




- docker build  通过Dockerfile文件创建



### 运行一个docker镜像

```
docker run  -d -p 8080:80 nginx  //运行成功后 访问 http://localhost:8080 就可以看到Nginx的欢迎界面
```




### 使用Dockerfile构建镜像
```
docker build  
```

### Docker的CS模式

docker的客户端与服务端通过  socket进行通信

unix
tcp
fd


### Docker 守护进程的配置和操作

-  使用 service命令管理
```
 sudo service docker start
 sudo service docker stop
 sudo service docker restart
```

### Docker远程访问
```
1.修改服务器和客户端  -H 选项的值  为 tcp
2.export DOCKER_HOST="tcp://xxxxxxxxx:端口"  (端口一般是2375)   //这种方式也可以让
```





## Dockerfile指令

- `FROM <image>   ` 指定基础镜像
- `MAINTAINER`  指定维护者信息
- `RUN <COMMAND>`  shell模式    , 每个RUN指令, 都会在上一个镜像上创建一个镜像
- `RUN [] ` exec模式
-` EXPOSE`  指定镜像暴露端口号, 在使用时需要手动开启端口(端口映射)
- `CMD []`   exec模式, 在容器启动时运行相应的命令
- `CMD command param1 param2` shell模式, 如果run时指定了命令, 则会覆盖dockerfile中的命令
- `ENTRYPOINT[]`
- `ENTRYPOINT `
- `ADD`   包含了类似tar的解压功能
- `COPY` 如果单纯复制文件, 推荐使用COPY
- `VOLUME`  添加卷
- `WORKDIR `  设置工作目录(一般使用绝对路径)
- `ENV`  设置环境变量
- `USER` 指定以哪个用户身份运行
- `ONBUILD` 镜像触发器(本次构建不会执行, 被子镜像依赖时, 在子镜像构建时会执行)





## Docker的构建过程
- 从基础镜像运行一个容器
- 执行一天命令, 对容器做出修改
- 执行类似docker commit的操作, 提交一个新的镜像层
- 再基于刚提交的镜像运行一个新容器
- 执行Dockerfile中的下一条指令, ......, 直至所有指令执行完毕.


会删除中间层容器, 但未删除中间层创建的镜像, 因此可以查看中间层镜像, 这样就可以调试.


## Docker构建缓存

- 不是使用构建缓存 `docker build --no-cache` , 也可以修改 ENV设置的缓存时间

- `docker history` 查看镜像构建过程
