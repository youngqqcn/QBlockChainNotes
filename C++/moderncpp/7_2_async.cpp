//yqq

#include <iostream>
#include <algorithm>
#include <string>
#include <thread>
#include <future>
#include <vector>
#include <cmath>

using namespace std;

std::vector<uint64_t> PrimeFacotrization(uint64_t n)
{
    std::vector<uint64_t> vctFactors;
    for (uint64_t i = 2; i <= sqrt(n); i++)
    {
        if (n % i == 0)
        {
            //printf("%llu  ", i);
            vctFactors.push_back(i);
            vctFactors.push_back( n / i );
        }
          
    }
    return std::move(vctFactors);
}

int main(int argc, char *argv[])
{
    if(argc < 2)
    {
        std::cout << "usage   ./a.out  number" << std::endl;
        return 0;
    }

    uint64_t  num = atoll(argv[1]);
    std::future<std::vector<uint64_t> >  result = std::async(PrimeFacotrization, num);

    PrimeFacotrization(num * 2);

    std::cout << "开始获取 aysnc函数的返回值" <<  std::endl;
    auto factors = result.get();
    std::for_each(factors.begin(), factors.end(), [](uint64_t n ){
        std::cout << n  << " ";
    });
    std::cout << std::endl;

    

    return 0;
}
