
/**
 * 2020-01-31
 * 
 * 如果只有一个全局变量 , 直接使用 static就可以解决初始化竞争的问题,  
 * 
 * 注意: 仅仅是解决 "初始化竞争",  而不能解决初始化后的 "资源竞争"
 * 
 * 
 */


#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <chrono>
#include <string>


class MySingleton
{
protected:

    MySingleton(){}
    ~MySingleton() {}

public:

    void Print()
    {
        std::cout << this << std::endl;
        std::cout << "this is singleton pattern" << std::endl;
    }

    /*virtual void ~Print()
    {
        std::cout << "~Print()" << std::endl;
    }*/

    static MySingleton * GetInstance()
    {
        /*
        static MySingleton *pInstance = nullptr;
        if(nullptr == pInstance)
        {
            pInstance = new MySingleton();  
        }
        return pInstance;
        */


        //参考:  https://chenxiaowei.gitbook.io/c-concurrency-in-action-second-edition-2019/3.0-chinese/3.3-chinese
        //在C++11后, 此过程是线程安全的. 所以不必再使用互斥量
        static MySingleton *pInstance = new MySingleton(); 
        return pInstance;
        
    }

};




#if 0
int main()
{
    std::cout << "new debug" << std::endl;
    MySingleton *pInst = MySingleton::GetInstance();
    MySingleton *pInst2 = MySingleton::GetInstance();
    pInst->Print();
    pInst2->Print();

    return 0;
}
#endif