/**
*Date: 2020/02/04 17:47
*Author:yqq
*Descriptions:none
*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#endif
#include <cstdio>
#include <iostream>
#include <atomic>
#include <thread>

using namespace std;

int main(void)
{
	int a = 99;

	int* pa = &a ;


	std::atomic<int*> atomicPtr(pa);

	std::cout << * atomicPtr.load() << std::endl;

	int b = 55;
	atomicPtr.store(  &b );
	std::cout << * atomicPtr.load() << std::endl;

	if (atomicPtr.is_lock_free())
	{
		std::cout << "is lock_free" << std::endl;
	}
	else
	{
		std::cout << "is not lock free" << std::endl;
	}


	//atomicPtr.fetch_add();

	int nArr[100]{0};
	for (int i = 0; i < sizeof(nArr) / sizeof(nArr[0]); i++)
	{
		nArr[i] = i * 10;
	}

	std::atomic<int*> pArr( nArr );

	int* pTmp =  pArr.fetch_add(3);  // ÏÈ·µ»ØpArr  ÔÚ += 3
	std::cout << *pTmp << std::endl;  
	std::cout << *pArr.load() << std::endl;





	

	std::cout << "hello world" << std::endl;
	return 0;
}