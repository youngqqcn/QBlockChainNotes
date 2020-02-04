#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <chrono>
#include <string>

using namespace std;

struct some_big_object
{
	std::string strName;
	std::string strAddr;
	int		nNo;
};

void swap(some_big_object& lhs, some_big_object& rhs)
{
	some_big_object tmp;
	tmp.nNo = lhs.nNo;
	tmp.strAddr = lhs.strAddr;
	tmp.strName = lhs.strName;
		
	lhs.nNo = rhs.nNo;
	lhs.strAddr = rhs.strAddr;
	lhs.strName = rhs.strName;

	rhs.nNo = tmp.nNo;
	rhs.strAddr = tmp.strAddr;
	rhs.strName = tmp.strName;

}

class X
{

private:
	some_big_object some_detail;
	std::mutex m;

public:
	X(some_big_object const& sd) :some_detail(sd) {}

#if 0
	friend void swap(X& lhs, X& rhs)
	{
		if (&lhs == &rhs)
			return;

		//传统方式: 手动管理
		std::cout << "starting lock two mutex" << std::endl;

		lhs.m.lock();
		rhs.m.lock();
		std::cout << "lock two mutex successed" << std::endl;

		swap(lhs.some_detail, rhs.some_detail);
		lhs.m.unlock();
		rhs.m.unlock();

		std::cout << "swaped successed." << std::endl;
	}
#elif 0

	friend void swap(X& lhs, X& rhs)
	{
		if (&lhs == &rhs)
			return;


		std::cout << "starting lock two mutex" << std::endl;

		std::lock(lhs.m, rhs.m); // 锁住两个互斥量

		std::cout << "lock two mutex successed" << std::endl;


		//将互斥量交由 std::lock_guard 来管理(释放锁)
		std::lock_guard<std::mutex> lock_a(lhs.m, std::adopt_lock); // 2
		std::lock_guard<std::mutex> lock_b(rhs.m, std::adopt_lock); // 3

		swap(lhs.some_detail, rhs.some_detail);

		std::cout << "swaped successed." << std::endl;
	}
#elif  0
	friend void swap(X& lhs, X& rhs)
	{
		if (&lhs == &rhs)
			return;

		std::cout << "starting lock two mutex" << std::endl;

		//在C++17中,  使用 scoped_lock 管理多个互斥量
		//构造即初始化(上锁)
		//析构时释放(解锁)
		std::scoped_lock   scopedlock(lhs.m, rhs.m);  //C++17

		swap(lhs.some_detail, rhs.some_detail);

		std::cout << "swaped successed." << std::endl;
	}

#else 
	friend void swap(X& lhs, X& rhs)
	{
		if (&lhs == &rhs)
			return;

		std::cout << "starting lock two mutex" << std::endl;


		//
		std::unique_lock<std::mutex> lock_a( lhs.m, std::defer_lock );
		std::unique_lock<std::mutex> lock_b( rhs.m, std::defer_lock );

		std::lock( lock_a, lock_b );


		swap(lhs.some_detail, rhs.some_detail);

		std::cout << "swaped successed." << std::endl;
	}

#endif


	friend std::ostream& operator << (std::ostream &outs, const X & x)
	{
		outs << "name:" << x.some_detail.strName << "; addr : "
			<< x.some_detail.strAddr << "; no:" << x.some_detail.nNo;
		return outs;
	}

};

#if 0

int main()
{

	X a(some_big_object{"ZhangSan", "BeiJing", 9});
	X b(some_big_object{"LiSi", "NanJing", 100});

	//a.m.lock();

#if 0
	swap(a, b);
#else
	std::cout << "before swap: " << std::endl;
	std::cout << "a ---> " << a << std::endl;
	std::cout << "b ---> " << b << std::endl;
	
	
	auto func = [&a , &b]() {
		//while (1)
		for(int i = 0; i < 10000; i++)
		{
			std::this_thread::sleep_for( std::chrono::microseconds(10) );
			swap(a, b);
		}
	};
	
	std::vector<std::thread> vctThds;

	for (int i = 0; i < std::thread::hardware_concurrency(); i++)
	{
		vctThds.emplace_back(  func  );
	}
	for (auto &thrd : vctThds)
	{
		thrd.join();
	}

#endif

	std::cout << "after swaped: " << std::endl;
	std::cout << "a ---> " << a << std::endl;
	
	std::cout << "b ---> " << b << std::endl;

	std::cout << "hello world" << std::endl;
	system("pause");
    return 0;
}
#endif