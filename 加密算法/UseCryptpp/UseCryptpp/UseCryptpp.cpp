// UseCryptpp.cpp : 定义控制台应用程序的入口点。
//
/**
*Date: 2018/12/29 0:26
*Author:yqq
*Descriptions:使用cryptopp库
*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#include <windows.h>
#endif


#include "stdafx.h"
#include "md5_test.h"
#include "aes_test.h"
#include "des_test.h"
#include "rsa_test.h"
#include "sha_test.h"


int main()
{
	//MD5_test();
	//aes_test();
	//aes_test_2();
	//des_test();
	//rsa_test();
	//sha_test();
	sha_test1();
	system("pause");
	return 0;
}