//yqq

#include <iostream>
#include <algorithm>
#include <string>
using namespace std;



class MyClass
{
private:
    /* data */
    int *_m_pData;
    std::string  _m_strName;
public:

    MyClass(const std::string  &strName)
    :_m_pData(new int(10)), _m_strName(strName)
    {
        std::cout << "construct " << _m_strName << std::endl;
    }

    MyClass(MyClass& rhs):
         _m_pData(new int(*(rhs._m_pData))),
        _m_strName(rhs._m_strName)
    {
        std::cout <<  "copy " << rhs._m_strName << std::endl;
    }

    MyClass(MyClass&& r_rhs): 
        _m_strName(r_rhs._m_strName),
        _m_pData(r_rhs._m_pData)
    {
        std::cout << " moved " << r_rhs._m_strName << std::endl;
        r_rhs._m_pData = nullptr;
        r_rhs._m_strName.clear();
    }

    ~MyClass()
    {
        std::cout << _m_strName <<  " ~MyClass() " << std::endl;
        delete _m_pData;
    }
};

// MyClass  foo(bool flag)
MyClass  foo(bool flag)
{
    //将亡值 (xvalue, expiring value)，
    //是 C++11 为了引入右值引用而提出的概念（因此在传统 C++
    //中，纯右值和右值是同一个概念），也就是即将被销毁、却能够被移动的值。
    // 移动了之后, 将忘值还是会销毁,
    // 
    // 这也解释了为什么会有 3 次析构

    MyClass  objA("A"), objB("B");
    if(flag) {
        std::cout << "a" << std::endl;
        return objA;
    } 
    else {
        std::cout << "b" << std::endl;
        return objB;
    }
}

/*
函数形参类型    实参参数类型    推导后函数形参类型
T&              左引用          T&
T&              右引用          T&
T&&             左引用          T&
T&&             右引用          T&&
*/

//无论模板参数是什么类型的引用，当且仅当实参类型为右引用且形参类型为右引用时,
//模板参数才能被推导为右引用类型。

int main()
{
    MyClass  a = foo(true);
    std::cout << "obj: "  << std::endl;

    return 0;
}
