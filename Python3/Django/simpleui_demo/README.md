





django simpleui demo.
---

<center>
<a href="https://github.com/newpanjing/simpleui">Simple UI源码</a> |
<a href="https://simpleui.88cto.com">Simple社区</a> 
</center>

simpleui demo,默认使用sqlite数据库。
启动步骤请查看下面的内容，如果你没有接触过django 或者 django admin，请先自己去django的官方查看相关文档学习。

simpleui 是一个django admin的ui框架，与代码无关。

# 自动安装
Linux或者macOS可以直接运行`bootstrap.sh`脚本，自动配置虚拟环境、安装依赖包、启动运行
```shell
sh ./bootstrap.sh
```

# 手动步骤

> <https://github.com/newpanjing/simpleui/blob/master/QUICK.md>

## 第一步
下载源码到本地
```shell
git clone https://github.com/newpanjing/simpleui_demo
```

## 第二步
安装依赖包

```shell
pip install -r requirements.txt
```

## 第三步
```shell
python manage.py runserver 8000 

#如果在服务器部署, 需要将静态资源复制到项目目录下
#https://github.com/newpanjing/simpleui/blob/master/QUICK.md#%E5%85%8B%E9%9A%86%E9%9D%99%E6%80%81%E6%96%87%E4%BB%B6%E5%88%B0%E6%A0%B9%E7%9B%AE%E5%BD%95
python manage.py collectstatic


# 如果在 CentOS 上部署,  会遇到 sqlite3版本过低,
# 方案) 升级 sqilte3即可
```

## 第四步
打开浏览器，在地址栏输入以下网址
> http://localhost:8000/admin

## 第五步
在用户名和密码的框框输入
+ 用户名：simpleui
+ 密码：demo123456





## nginx + uwsgi 部署

[nginx+uwsgi部署.md](./nginx+uwsgi部署.md)






## PS
+ 有任何疑问请加入QQ群：786576510
+ 或者前往社区提问搜索答案：[Simple社区](https://simpleui.88cto.com)