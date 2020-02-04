/**
*Date: 2020/01/11 15:28
*Author:yqq
*Descriptions:   c++11   thread ´«²Î
*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#endif
#include <cstdio>
#include <iostream>
#include <thread>
#include <string>


using namespace std;



void MyPrintThreadProc(int n, const char *pszTmp)
{
	std::cout << "n" << n << "str: " << pszTmp;
}


int main(void)
{
	const char *pszTmp  = "hwllo";
	int n = 999;
	std::thread t1(MyPrintThreadProc, n, pszTmp);

	t1.join();
	

	std::cout << "hello world" << std::endl;
	return 0;
}