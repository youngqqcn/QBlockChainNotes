// UseSQLite3.cpp : 定义控制台应用程序的入口点。
#define _CRT_SECURE_NO_WARNINGS  

/**
*Date: 2018/12/02 18:32
*Author:yqq
*Descriptions:  

	操作 sqlite3 数据库, 

	1.创建数据库
	2.增删改查
		
*/


#include "stdafx.h"
#include "sqlite3.h"
#include <iostream>

#pragma comment(lib, "sqlite3.lib")  //静态库

using namespace std;

sqlite3 * pDB = NULL;

//增加用户
bool AddUser(const string& sName, const string& sAge);
//删除用户
bool DeleteUser(const string& sName);
//修改用户
bool ModifyUser(const string& sName, const string& sAge);
//查找用户
bool SelectUser();

//创建user表
bool Create();

int _tmain(int argc, _TCHAR* argv[])
{
	//打开路径采用utf-8编码
	//如果路径中包含中文，需要进行编码转换
	int nRes = sqlite3_open("testDB.db", &pDB); //ok
	if (nRes != SQLITE_OK)
	{
		cout << "Open database fail: " << sqlite3_errmsg(pDB);
		goto QUIT;
	}
	//创建user表
	if (!Create())
	{
		goto QUIT;
	}

	//添加“赵钱孙李”
	if (!AddUser("zhao", "18")
		|| !AddUser("qian", "19")
		|| !AddUser("sun", "20")
		|| !AddUser("li", "21"))
	{
		goto QUIT;
	}

	//删除“赵”
	if (!DeleteUser("zhao"))
	{
		goto QUIT;
	}

	//修改“孙”
	if (!ModifyUser("sun", "15"))
	{
		goto QUIT;
	}

	//查找用户
	if (!SelectUser())
	{
		goto QUIT;
	}

QUIT:
	sqlite3_close(pDB);

	system("pause");
	return 0;
}

bool Create()
{
	std::string strSql = "";
	//strSql += "create table if not exists user(\
		id int(10) primary key AUTO_INCREMENT  not null,\
		name varchar(100) not null\
		);";  // 如果不存在user 表, 则创建 user表 

	//注意: sqlite 创建表的方式   和  mysql 稍微不同
	strSql += "create table if not exists user(  \
		id integer primary key autoincrement,\
		name varchar(64),\
		age integer\
		);";

	char *pszErrMsg = NULL;
	int nRet = sqlite3_exec(pDB, strSql.c_str(), 0, 0, &pszErrMsg);
	if (SQLITE_OK != nRet)
	{
		std::cout << "创建表失败:" << pszErrMsg  << std::endl;
		return false;
	}
	std::cout << "创建表 成功!" << std::endl;


	return true;
}

bool AddUser(const string& sName, const string& sAge)
{
	string strSql = "";
	strSql += "insert into user(name,age)";
	strSql += "values('";
	strSql += sName;
	strSql += "',";
	strSql += sAge;
	strSql += ");";

	char* cErrMsg;
	int nRes = sqlite3_exec(pDB, strSql.c_str(), 0, 0, &cErrMsg);
	if (nRes != SQLITE_OK)
	{
		cout << "add user fail: " << cErrMsg << endl;
		return false;
	}
	else
	{
		cout << "add user success: " << sName.c_str() << "\t" << sAge.c_str() << endl;
	}

	return true;
}

bool DeleteUser(const string& sName)
{
	string strSql = "";
	strSql += "delete from user where name='";
	strSql += sName;
	strSql += "';";

	char* cErrMsg;
	int nRes = sqlite3_exec(pDB, strSql.c_str(), 0, 0, &cErrMsg);
	if (nRes != SQLITE_OK)
	{
		cout << "delete user fail: " << cErrMsg << endl;
		return false;
	}
	else
	{
		cout << "delete user success: " << sName.c_str() << endl;
	}

	return true;
}

bool ModifyUser(const string& sName, const string& sAge)
{
	string strSql = "";
	strSql += "update user set age =";
	strSql += sAge;
	strSql += " where name='";
	strSql += sName;
	strSql += "';";

	char* cErrMsg;
	int nRes = sqlite3_exec(pDB, strSql.c_str(), 0, 0, &cErrMsg);
	if (nRes != SQLITE_OK)
	{
		cout << "modify user fail: " << cErrMsg << endl;
		return false;
	}
	else
	{
		cout << "modify user success: " << sName.c_str() << "\t" << sAge.c_str() << endl;
	}

	return true;
}

static int UserResult(void *NotUsed, int argc, char **argv, char **azColName)
{
	for (int i = 0; i < argc; i++)
	{
		cout << azColName[i] << " = " << (argv[i] ? argv[i] : "NULL") << ", ";
	}
	cout << endl;

	return 0;
}

bool SelectUser()
{
	char* cErrMsg;
	int res = sqlite3_exec(pDB, "select * from user;", UserResult, 0, &cErrMsg);

	if (res != SQLITE_OK)
	{
		cout << "select fail: " << cErrMsg << endl;
		return false;
	}

	return true;
}
