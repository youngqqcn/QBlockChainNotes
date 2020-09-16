//yqq

#include <iostream>
#include <algorithm>

using namespace std;


template <typename Arg1, typename Arg2> 
auto add(Arg1 arg1, Arg2 arg2) -> decltype(arg1 + arg2)  //C++11
{
    return arg1 + arg2;
}

template <typename Arg1, typename Arg2>
auto add_cpp17(Arg1 arg1, Arg2 arg2)  // C++14 
{
    return arg1 + arg2;
}

template<typename T = int, typename U = int>
auto add_default(T x, U y) -> decltype(x+y) { //c++11   默认模板参数
    return x+y;
}

int main()
{
    auto r = add<int, double>(1, 1.234);
    auto r2 = add_cpp17<int, double>(1, 1.234);
    auto r3 = add_default(9, 20);
    std::cout << r << std::endl;
    std::cout << r2 << std::endl;
    std::cout << r3 << std::endl;
    return 0;
}
