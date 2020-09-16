//yqq

#include <iostream>
#include <algorithm>
#include <string>
#include <memory>

using namespace std;

// std::shared_ptr/std::unique_ptr/std::weak_ptr

void foo(std::shared_ptr<std::string> &sp)
{
    *sp += std::string("good");
}


// 循环引用
struct A;
struct B;

struct A
{
    std::shared_ptr<B> pointer;
    // std::weak_ptr<B> pointer;
    A(){std::cout << "A 构造" << std::endl;}
    ~A()
    {
        std::cout << "A 被销毁" << std::endl;
    }
};
struct B
{
    std::shared_ptr<A> pointer;
    // std::weak_ptr<A> pointer;
    B(){std::cout << "B 构造" << std::endl;}
    ~B()
    {
        std::cout << "B 被销毁" << std::endl;
    }
};

int main()
{

    std::shared_ptr<std::string> sp = std::make_shared<std::string>("hello");
    // sp.get();
    std::cout << *sp << std::endl;
    // auto ssp = sp;
    foo(sp);
    std::cout << *sp << std::endl;

    std::unique_ptr<std::string> up = std::make_unique<std::string>("hello"); // c++14

    /*
    // unique_ptr  禁用了 拷贝构造  和  赋值运算符重载
      unique_ptr(const unique_ptr&) = delete;
      unique_ptr& operator=(const unique_ptr&) = delete;
    */
    // auto uup =  up;

    auto a = std::make_shared<A>();
    auto b = std::make_shared<B>();
    a->pointer = b; 
    //b 的引用计数变为 2
    b->pointer = a;
    //a 的引用计数变为 2

    return 0;
} // a , b 的引用计数减 1, 
