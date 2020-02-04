#include <iostream>
#include <future>
#include <thread>
#include <string>
#include <memory>
#include <chrono>
#include <cmath>


using namespace std;


double square_root(double x)
{
  if(x<0)
  {
    throw std::out_of_range("x<0");
  }
  return sqrt(x);
}

#if 0
int main()
{
    /**
     *  launch::async表示开启一个新的线程执行fn
        launch::deferred 表示fn推迟到future::wait/get时才执行
        launch::async|launch::deferred表示由库自动选择哪种机制执行fn，和第一种构造方式async(fn,args)策略相同
     */
    std::future<double> f=std::async(square_root, 9);

    std::cout << "doing other things..." << std::endl;

    for(int i = 0; i < 1000; i++)
    {
        std::cout << "other thing" << std::endl;
    }


    double y = f.get();

    std::cout << "reuslt = "  << y << std::endl;


    return 0;
}
#endif