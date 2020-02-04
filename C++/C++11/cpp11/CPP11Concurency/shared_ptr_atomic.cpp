/**
*Date: 2020/02/04 19:01
*Author:yqq
*Descriptions:
	
	1.多个线程可以读写不同shared_ptr(副本)(即使shared_ptr指向同一个对象)
	2.多个线程可以读取同一个 shared_ptr
	3.多个线程不能写同一个shared_ptr , 除非使用 原子函数, 如:  std::atomic_load  std::atomic_store


*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#endif
#include <cstdio>
#include <iostream>
#include <atomic>
#include <thread>
#include <memory>
#include <chrono>
#include <vector>

using namespace std;

struct  Printer
{
	int m_nA = 0;

	Printer(int a) : m_nA(a)
	{
	}

	void Show()
	{
		//std::this_thread::sleep_for( std::chrono::microseconds(100) );
		std::cout << "thread " << std::this_thread::get_id() << " m_nA: " << m_nA << std::endl;
		std::cout << this << std::endl;
		this->m_nA = 99;
	}
};


std::shared_ptr<Printer>  g_Data;

void ProcessGlobalData()
{
	while (nullptr == g_Data);

	//for (int i = 0; i < 10; i++)
	while(1)
	{
		//shared_ptr<Printer> spData = std::atomic_load( &g_Data);
		shared_ptr<Printer> spData = g_Data;
		spData->Show();
	}
}

#if 0
void UpdateGlobalData()
{
	for (int i = 0; i < 10; i++)
	{
		std::this_thread::sleep_for( std::chrono::microseconds(1) );
		std::shared_ptr<Printer> spTmp = std::make_shared<Printer>( i );
		std::atomic_store( &g_Data, spTmp );
	}
}
#endif

#if 0

//多个线程读取同一个  shared_ptr
void UpdateGlobalData()
{
	std::shared_ptr<Printer> spTmp = std::make_shared<Printer>(9999);
	g_Data = spTmp;
	for (int i = 0; ; )
	{
		std::this_thread::sleep_for(std::chrono::microseconds(1));
		spTmp->m_nA = i;
	}
}
#endif

//多个线程写同一个  shared_ptr
void UpdateGlobalData()
{
	//std::shared_ptr<Printer> spTmp = std::make_shared<Printer>(9999);
	for (int i = 0; ; )
	{
		//g_Data = spTmp;
		if (nullptr == g_Data)
		{
			std::shared_ptr<Printer> spTmp = 
			g_Data = std::make_shared<Printer>(9999);
		}

		std::cout << "hello" << std::endl;
		g_Data->Show();
	}
}


//多个线程写同一个  shared_ptr
void UpdateGlobalDataToNullptr()
{
	for (int i = 0; ; )
	{
		g_Data = nullptr;
	}
}



int main(void)
{
	std::vector<std::thread>  vctThreads;

#if 0
	vctThreads.emplace_back( UpdateGlobalData );

	//多个线程读取同一个  shared_ptr
	vctThreads.emplace_back( ProcessGlobalData );
	vctThreads.emplace_back( ProcessGlobalData );
	vctThreads.emplace_back( ProcessGlobalData );
	vctThreads.emplace_back( ProcessGlobalData );
#endif


	vctThreads.emplace_back( UpdateGlobalData );
	vctThreads.emplace_back( UpdateGlobalData );
	vctThreads.emplace_back( UpdateGlobalData );
	vctThreads.emplace_back( UpdateGlobalData );
	vctThreads.emplace_back( UpdateGlobalDataToNullptr );
	
	for (auto& thd : vctThreads)
	{
		thd.join();
	}

	std::cout << "hello world" << std::endl;
	return 0;
}