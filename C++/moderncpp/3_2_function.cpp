//yqq

#include <iostream>
#include <algorithm>
#include <functional>

using namespace std;


int foo(int n)
{
    return n;
}

void increase(int & v) {
    v++;
}

int main()
{
    std::function<int(int)> f = foo;
    std::cout << f(9) << std::endl;

    std::function<int(int)> func = [d = 9](int value) -> int {
        return d + value;
    };
    std::cout << func(9) << std::endl;


    auto add  = [](auto a, auto b, auto c) -> auto{
        return a + b + c;
    };

    auto bf = std::bind(add, std::placeholders::_1, 100, 200 );
    std::cout << bf(80) << std::endl;


    // double s = 1;
    // increase(s);

    return 0;
}
