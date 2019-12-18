# MongoDB

## 基本概念

- 数据库(database)
- 集合(collections)
- 文档(document)

## 基本命令

```sql
show dbs;#查看数据库
use test;#如果没有就创建一个
db;#查看当前数据库
db.dropDatabase();#删除数据库
show collections；#查看集合
```



## 增删改查

### 创建集合、插入：

```sql
create collection;#创建集合
db.student.insert({"name":"张三","age":"22","sex":"男","class":"计算机2班"});#如果数据库中不存在集合，就创建并插入这些数据
db.student.insert({"name":"李四","age":"22","sex":"女","phone":"18513081650","class":"计算机1班"});#里面的key-value不用保持一致
db.student.insert([{"name":"王五","age":"22","sex":"男","class":"计算机2班"},{"name":"赵六","age":"22","sex":"女","phone":"18513081650","class":"计算机1班"}]);#同时插入多条数据
```

###  更新：

```sql
db.student.update({"name":"张三"},{"name":"张三丰"});#如果有多条语句，只修改第一条，会覆盖原有数据
db.student.update({"22":"女"},{"name":"张三丰"});
db.student.update({"name":"张三"},{$set:{"name":"张无忌"}});#只想改某个key的value使用set
db.student.update({"name":"王五"},{$set:{"name":"张无忌"}},{multi:true});#把所有的记录都改了
```

### 查询：	

```sql
db.student.find();#查询全部
db.student.find({"name":"李四"});#查询指定记录，返回这一行结果
db.student.update({"name":"张三丰"},{"name":"张无忌","age":"28","sex":"男"});
db.student.find({"name":"张无忌","age":"28"});#and操作
db.student.find({$or:[{"name":"张无忌"},{"name":"李四"}]});#or操作
db.student.find().pretty();#格式化显示
db.student.find().count();#获取结果的行数
db.student.find().sort({"age":-1});#按照sort里面key的值排序，1为正序，-1为倒序
```


### 删除：

```sql
db.student.remove();#删除所有数据
db.student.remove({"22":"女"});#按照条件删除
db.student.remove({"name":"张无忌"},2);#删除几条
```

## 文档之间的关系

- 1-1 关系   (可以通过内嵌文档方式实现, 也可以通过唯一id方式实现)
- 1-n (或n-1) 关系  (可以通过内嵌文档方式实现, 也可以通过id数组方式实现)
- n-m 关系 (可以通过  id数组方式实现)





## C++使用(Windows/linux)