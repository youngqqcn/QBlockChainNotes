// TestMysql.cpp : Defines the entry point for the console application.
//

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
