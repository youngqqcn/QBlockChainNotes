# mysql学习笔记


## MySQL存储引擎

| 特性| InnoDB | MyISAM | MEMORY|
|--|--|--|--|
|事务安全 | 支持 |无 | 无 |
|存储限制| 64TB| 有 | 有|
|空间使用| 高| 低| 低 |
|内存使用| 高| 低| 高 |
|插入数据的速度| 慢| 快| 快|
|对外键的支持|支持 | 无 | 无 |


## 三大存储引擎的使用场景

### InnoDB
- 支持事务，是事务安全的（事务的介绍移驾 [数据库事务](http://blog.csdn.net/cool_wayen/article/details/78890949) ），提供行级锁与外键约束，有缓冲池，用于缓冲数据和索引
- 适用场景：用于事务处理，具有ACID事物支持，应用于执行大量的`insert`和`update`操作的表

### MyISAM
- 不支持事务，不支持外键约束，不支持行级锁，操作时需要锁定整张表，不过会保存表的行数，所以当执行`select count(*) from tablename`时执行特别快
- 适用场景：用于管理非事务表，提供高速检索及全文检索能力，适用于有大量的`select`操作的表，如 日志表

### MEMORY

- 使用存在于内存中的内容创建表，每一个memory只实际对应一个磁盘文件。因为是存在内存中的，所以memory访问速度非常快，而且该引擎使用hash索引，可以一次定位，不需要像B树一样从根节点查找到支节点，所以精确查询时访问速度特别快，但是非精确查找时，比如`like`，这种范围查找，hash就起不到作用了。**另外一旦服务关闭，表中的数据就会丢失，因为没有存到磁盘中。**

- 适用场景：主要用于内容变化不频繁的表，或者作为中间的查找表。对表的更新要谨慎因为数据没有被写入到磁盘中，服务关闭前要考虑好数据的存储




## MySQL常用操作

### 连接数据库
```sql
mysql -h localhost -u root -p
```

### 创建数据库

```sql
create database 数据库名;
```


### 删除数据库

```sql
drop database 数据库名 ;
```

### 选择数据库

```sql
use 数据库名;
```


### 创建数据表

```sql
CREATE TABLE IF NOT EXISTS `runoob_tbl`(
   `runoob_id` INT UNSIGNED AUTO_INCREMENT,
   `runoob_title` VARCHAR(100) NOT NULL,
   `runoob_author` VARCHAR(40) NOT NULL,
   `submission_date` DATE,
   PRIMARY KEY ( `runoob_id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
```


### 删除数据表

```sql
DROP TABLE table_name ;
```

### 插入数据

```sql
INSERT INTO runoob_tbl
   (runoob_title, runoob_author, submission_date)
   VALUES
   ("学习 PHP", "菜鸟教程", NOW());
```


### 查询数据

```sql
SELECT column_name,column_name
FROM table_name
[WHERE Clause]
[LIMIT N][ OFFSET M]
```


### where子句

```sql
SELECT field1, field2,...fieldN FROM table_name1, table_name2...
[WHERE condition1 [AND [OR]] condition2.....
```

### update

```SQL
UPDATE table_name SET field1=new-value1, field2=new-value2
[WHERE Clause]
```


### delete

```SQL
DELETE FROM table_name [WHERE Clause]
```


### like

```sql
SELECT field1, field2,...fieldN
FROM table_name
WHERE field1 LIKE condition1 [AND [OR]] filed2 = 'somevalue'
```

### ALTER命令
- 删除，添加或修改表字段
```sql
ALTER TABLE testalter_tbl  DROP i;
ALTER TABLE testalter_tbl ADD i INT;
```
- 修改字段类型及名称
```sql
ALTER TABLE testalter_tbl MODIFY c CHAR(10);
 ALTER TABLE testalter_tbl CHANGE i j BIGINT;  //将字段i 改名为 j  类型改为 BIGINT
```

- ALTER TABLE 对 Null 值和默认值的影响
```SQL
ALTER TABLE testalter_tbl  MODIFY j BIGINT NOT NULL DEFAULT 100;
ALTER TABLE testalter_tbl ALTER i DROP DEFAULT; //删除某列的默认值
```
- 修改字段默认值
```sql
 ALTER TABLE testalter_tbl ALTER i SET DEFAULT 1000;
```

- 修改表名
```sql
 ALTER TABLE testalter_tbl RENAME TO alter_tbl;
```


###  视图

#### view的概念
- view又称虚拟表, view是sql的查询结果.

#### 用途
- 1.权限控制, 即可以通过视图开放其中一列或几列.
- 2.简化复杂的查询


### 视图的更新 , 删除, 添加

- 如果视图的每一行与物理是一一对应的关系,可以更新.
否则不可以更新.

### 视图的内部原理

- 对于简单查询的view, 会把键视图的语句合并为一条查表语句.  merge

- 对于复杂的view, 会先执行创建视图的语句形成一张临时表, 然后再查临时表.   temptable





## 常用管理语句

```sql
查看所有表    show tables
查看表结构    desc 表名/视图名
查看建表过程   show create table
查看表信息    show table  表名   status
删除表       drop  table  表名
删除视图     drop  view  视图名
改表名       rename   table oldName to newName
清空表数据   truncate

```


```sql
show create table 表名;   //查看建表过程
show create view 视图名;  //查看建视图过程
show  table status;
show table status where name=表名;
rename  table  oldTable  newTable;
delete from 表名;
```


## 字符集与乱码问题


```sql
set names  utf8;  //设置  client  results  connecttion  都为gbk编码
```



## 索引
索引用来定位行数据的位置.

key  普通索引
unique key   唯一索引
primary key  主键索引
fulltext  全文索引 (中文可用sphinx)


```SQL
show index  from 表名;
```


在MyISAM引擎
- `.frm是表信息文件`
- `.MYD`是数据文件
- `.MYI`是索引文件


## 事务

ACID原则

- 原子性：一个事务（transaction）中的所有操作，要么全部完成，要么全部不完成，不会结束在中间某个环节。事务在执行过程中发生错误，会被回滚（Rollback）到事务开始前的状态，就像这个事务从来没有执行过一样。

- 一致性：在事务开始之前和事务结束以后，数据库的完整性没有被破坏。这表示写入的资料必须完全符合所有的预设规则，这包含资料的精确度、串联性以及后续数据库可以自发性地完成预定的工作。

- 隔离性：数据库允许多个并发事务同时对其数据进行读写和修改的能力，隔离性可以防止多个事务并发执行时由于交叉执行而导致数据的不一致。事务隔离分为不同级别，包括读未提交（Read uncommitted）、读提交（read committed）、可重复读（repeatable read）和串行化（Serializable）。

- 持久性：事务处理结束后，对数据的修改就是永久的，即便系统故障也不会丢失。


```sql
BEGIN  或 START TRANSACTION  ; //开始事务
ROLLBACK  //回滚
COMMIT //事务提交

```




## C++操作mysql

```cpp
#include "stdafx.h"
#include<iostream>
#include<Windows.h>
#include <mysql.h>
#include<string>
#pragma  comment(lib, "../lib/libmysql.lib")
using namespace std;

int main()
{

	//必备的一个数据结构
	MYSQL mydata;

	//初始化数据库
	if (0 == mysql_library_init(0, NULL, NULL)) {
		cout << "mysql_library_init() succeed" << endl;
	}
	else {
		cout << "mysql_library_init() failed" << endl;
		return -1;
	}

	//初始化数据结构
	if (NULL != mysql_init(&mydata)) {
		cout << "mysql_init() succeed" << endl;
	}
	else {
		cout << "mysql_init() failed" << endl;
		return -1;
	}

	//在连接数据库之前，设置额外的连接选项
	//可以设置的选项很多，这里设置字符集，否则无法处理中文
	if (0 == mysql_options(&mydata, MYSQL_SET_CHARSET_NAME, "gbk")) {
		cout << "mysql_options() succeed" << endl;
	}
	else {
		cout << "mysql_options() failed" << endl;
		return -1;
	}

	//连接数据库
	if (NULL
		!= mysql_real_connect(&mydata, "localhost", "root", "12345678", "test",
			3306, NULL, 0))
		//这里的地址，用户名，密码，端口可以根据自己本地的情况更改
	{
		cout << "mysql_real_connect() succeed" << endl;
	}
	else {
		cout << "mysql_real_connect() failed" << endl;
		system("pause");
		return -1;
	}

	//sql字符串
	string sqlstr;

	//创建一个表
	sqlstr = "CREATE TABLE IF NOT EXISTS `new_paper` (";
	sqlstr += " `NewID` int(11) NOT NULL AUTO_INCREMENT,";

	sqlstr += " `NewCaption` varchar(40) NOT NULL,";

	sqlstr += " `NewContent` text,";

	sqlstr += " `NewTime` DATE DEFAULT NULL,";

	sqlstr += " PRIMARY KEY(`NewID`)";

	sqlstr += " ) ENGINE = InnoDB DEFAULT CHARSET = utf8";


	if (0 == mysql_query(&mydata, sqlstr.c_str())) {
		cout << "mysql_query() create table succeed" << endl;
	}
	else {
		cout << "mysql_query() create table failed" << endl;
		mysql_close(&mydata);
		return -1;
	}


	//向表中插入数据
	for (int i = 0; i < 100; i++)
	{
		sqlstr =
			"INSERT INTO `test`.`new_paper` (`NewID`, `NewCaption`, `NewContent`, `NewTime`) ";
		sqlstr += "VALUES (default, '测试', '这一些描述', NOW());";
		if (0 == mysql_query(&mydata, sqlstr.c_str())) {
			cout << "mysql_query() insert data succeed" << endl;
		}
		else {
			cout << "mysql_query() insert data failed" << endl;
			mysql_close(&mydata);
			return -1;
		}
	}

	//显示刚才插入的数据
	//sqlstr = "SELECT `NewID`,`NewCaption`,`NewContent`,`NewTime` FROM `test`.`new_paper`";
	sqlstr = "SELECT * FROM `test`.`new_paper`";
	MYSQL_RES *result = NULL;
	if (0 == mysql_query(&mydata, sqlstr.c_str())) {
		cout << "mysql_query() select data succeed" << endl;

		//一次性取得数据集
		result = mysql_store_result(&mydata);
		//取得并打印行数
		int rowcount = mysql_num_rows(result);
		cout << "row count: " << rowcount << endl;

		//取得并打印各字段的名称
		unsigned int fieldcount = mysql_num_fields(result);
		MYSQL_FIELD *field = NULL;
		for (unsigned int i = 0; i < fieldcount; i++) {
			field = mysql_fetch_field_direct(result, i);
			cout << field->name << "\t\t";
		}
		cout << endl;

		//打印各行
		MYSQL_ROW row = NULL;
		row = mysql_fetch_row(result);
		while (NULL != row) {
			for (int i = 0; i < fieldcount; i++) {
				cout << row[i] << "\t\t";
			}
			cout << endl;
			row = mysql_fetch_row(result);
		}

	}
	else {
		cout << "mysql_query() select data failed" << endl;
		mysql_close(&mydata);
		return -1;
	}


#if 1
	//删除刚才建的表
	sqlstr = "DROP TABLE `test`.`new_paper`";
	if (0 == mysql_query(&mydata, sqlstr.c_str())) {
		cout << "mysql_query() drop table succeed" << endl;
	}
	else {
		cout << "mysql_query() drop table failed" << endl;
		mysql_close(&mydata);
		return -1;
	}
#endif

	mysql_free_result(result);
	mysql_close(&mydata);
	mysql_server_end();

	system("pause");
	return 0;
}


```
