/**
*Date: 2020/02/02 18:04
*Author:yqq
*Descriptions:none
*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#endif
#include <cstdio>
#include <iostream>
#include <atomic>

using namespace std;

int main(void)
{
	std::atomic_flag   atom_flag;// = ATOMIC_FLAG_INIT;
	if (!atom_flag.test_and_set(std::memory_order_acquire))
	{
		std::cout << "setted" << std::endl;
	}
	else
	{
		//if (atom_flag.test_and_set(std::memory_order_acquire)) //error
		atom_flag.clear();
		if (!atom_flag.test_and_set(std::memory_order_acquire))
		{
			std::cout << "setted" << std::endl;
		}
		std::cout << "not setted" << std::endl;
	}


	std::atomic<bool>  bFlag = false;
	bool bExpected = true;
	bFlag.compare_exchange_strong( bExpected, false); //如果bFlag当前的值与bExpected不同, 则将 

	std::cout << ((bFlag) ? ("true") : ("false") )<< std::endl;



	

	std::cout << "hello world" << std::endl;
	return 0;
}