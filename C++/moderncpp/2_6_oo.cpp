//yqq

#include <iostream>
#include <algorithm>

using namespace std;


class Base
{
public:
    int _m_v1;
    int _m_v2;

    Base()
    {
        _m_v1 = 1;
    }

    Base(int n) : Base() //C++11 委托构造
    {
        _m_v2 = n;
    }

    virtual void FinalFunc() final
    {
        std::cout << "this is final function" << std::endl;
    }

};


class Sub : public Base
{
public:
    int _m_v3;
    Sub(int v3):Base(2)
    {
        _m_v3 = v3;
    }

    // virtual void FinalFunc() 
    // {
    //    std::cout << "override final function" << std::endl; 
    // }

    
public:
    using Base::Base;
};


class MyClass
{
public:
    MyClass() = default;
    MyClass& operator=(const MyClass& ) = delete;
    MyClass(int n) {std::cout << n << std::endl; };
};


int main()
{
    Base b(9);

    std::cout << b._m_v1 << std::endl;
    std::cout << b._m_v2 << std::endl;


    Sub s(9);
    std::cout <<" ---------" << std::endl;
    std::cout << s._m_v1 << std::endl;
    std::cout << s._m_v2 << std::endl;
    std::cout << s._m_v3 << std::endl;
    std::cout <<" ---------" << std::endl;

    MyClass mcls(99);

    return 0;
}
