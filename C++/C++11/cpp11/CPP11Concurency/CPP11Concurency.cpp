// CPP11Concurency.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <thread>
#include <chrono>


void thread_proc()
{
	for (int i = 0; i < 10; i++)
	{
		std::cout << "thread :" << std::this_thread::get_id() << std::endl;
		std::this_thread::sleep_for( std::chrono::microseconds(10) );
	}

}


struct Functor
{
	char* m_pEchoStr = nullptr;
	
	void operator()()
	{
		for (int i = 0; i < 10; i++)
		{
			sprintf(m_pEchoStr, "ehco : %d", i);
			std::cout << "Functor :" << std::this_thread::get_id() << "   echo str:" << m_pEchoStr << std::endl;
			std::this_thread::sleep_for(std::chrono::microseconds(10));
		}

	}
};



int main()
{

	//1.通过普通函数, 作为thread的构造函数参数, 创建线程

	std::thread  t1(thread_proc); //创建并立即启动线程
	//t1.join();
	t1.detach();
	
	if (!t1.joinable())  //如果线程已经detach, 则joinable为false 
	{
		std::cout << "can't join thread  " << t1.get_id() << std::endl;
	}



	//2.使用仿函数(函数对象) 作为thread构造函数参数, 创建线程
	//int n = 999999999;
	//std::string  strTmp("hello world");
	//functor.m_pEchoStr = strTmp.c_str();

	char szBuf[1024] = "hello world";
	Functor functor;
	functor.m_pEchoStr = szBuf;
	std::thread  t2(functor);
	t2.join();
	//t2.detach();   //!!!!特别注意:  detach 需要注意  线程参数的生命周期, 否则会发生不可预料的错误



	//3.使用lambda函数作为thread构造函数的参数, 创建线程
	std::thread  t3([&]() {
		for (int i = 0; i < 5; i++)
		{
			sprintf(szBuf, "this is lamdba %d", i);
			std::cout << "lambda : " << i << " ------>" << szBuf << std::endl;;
		}
	});
	t3.join();




    std::cout << "Hello World!\n";
}
