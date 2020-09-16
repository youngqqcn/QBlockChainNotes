//yqq

#include <iostream>
#include <algorithm>
// #include <utility>
#include <memory>
using namespace std;

int main()
{
    int value = 1;

    // 值捕获 与参数传值类似，值捕获的前提是变量可以拷贝，
    // 不同之处则在于，被捕获的变量在 lambda
    // 表达式被创建时拷贝，而非调用时才拷贝
    auto foo = [=] {  // 
        return value;
    };

    value = 9;
    auto value2  = foo();
    std::cout << "value = " << value << std::endl;
    std::cout << "value2 = " << value2 << std::endl;


    int  a = 0;
    auto func = [a](int v) {
        v = a + 1;
        return v;
    };
    auto b = func(a);
    auto c = a;
    std::cout << "b = " << b << std::endl;  // 1
    std::cout << "c = " << c << std::endl;  // 0


    int x  = 0;
    auto fun = [&x](int n) -> int&{
        x += 1 + n;
        return x;
    };
    x++; 
    auto y = fun(x); 
    auto& z = fun(x); 
    y++; 
    z++; 
    std::cout << "x = " << x << std::endl;  
    std::cout << "y = " << y << std::endl; 
    std::cout << "z = " << z << std::endl;  


    auto ptr = std::make_unique<int>(9);
    auto add = [v1 = 1, v2 = std::move(ptr)](int x, int y) {
    // auto add = [v1 = 1, v2 = ptr](int x, int y) { // error unique_ptr 不可拷贝
        return x + y + v1 + (*v2);
    };
    std::cout << add(9, 10) << std::endl;



    auto f = [](auto x, auto y) -> auto { //C++14
        return x + y;
    };
    std::cout << f(9, 2) << std::endl;


    return 0;
}
