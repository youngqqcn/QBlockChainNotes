//yqq

#include <iostream>
#include <algorithm>
#include <string>
#include <future>
#include <thread>
#include <cmath>
#include <chrono>
using namespace std;


//辗转相除法求最大公约数函数
int gcd(int a, int b) {
	int temp;

	//比较两个数的大小，值大的数为a，值小的数为b
	if (a < b) {
		temp = a;
		a = b;
		b = temp;
	}

	//求余
	while (b != 0) {
		temp = a % b;
		a = b;
		b = temp;
	}
	return a;
}


int main()
{
    std::packaged_task<double ( double )> task([](double n)->double {
        std::this_thread::sleep_for(std::chrono::seconds(10));
        return sqrt(n); 
    });


    // std::function<>
    //std::packaged_task<int (int, int)> gcdTask([](int, int));
    std::packaged_task<int (int, int)>  gcdTask(gcd);

    std::future<double> result = task.get_future();
    std::future<int> gcdResult = gcdTask.get_future();
    std::thread(std::move(gcdTask), 23782349, 7282335).detach();

    std::thread(std::move(task), 9.9234).detach();
    std::cout << "do othering" << std::endl;
    for(int i = 0; i < 100; i++)
    {
        double sum = i * 3.1234234329;
        std::cout << sum << std::endl;
        //std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    std::cout << "gcd result: " << gcdResult.get() << std::endl;

    std::cout << "get result" << std::endl;
    if( result.valid())    
    {
        std::cout << "result is valid" << std::endl;
        std::cout << "result is :" << result.get() << std::endl;  // get() 会阻塞等待, 知道结果返回
    }
    else
    {
        std::cout << "result is invalid" << std::endl;
    }
    


    return 0;
}
