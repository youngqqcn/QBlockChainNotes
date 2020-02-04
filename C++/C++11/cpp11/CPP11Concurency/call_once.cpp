
/*


使用 std::call_once  和 std::once_flag 解决资源初始化多线程竞争问题

*/


#include <iostream>
#include <thread>
#include <mutex>
#include <string>
#include <chrono>
#include <vector>
#include <sstream>

using namespace std;


struct Printer
{
private:
    std::once_flag  __m_initFlag;

    void Init()
    {
        std::cout << "starting init printer" << std::endl;

        std::cout << "init finished." << std::endl;
    }

public:

    void Print( const std::string &strInput)
    {
        std::call_once( __m_initFlag, &Printer::Init, this );
        for(int i = 0; i < 10; i++)
        {
            std::ostringstream fmts;
            std::thread::id  tid = std::this_thread::get_id();
            
            fmts  << "thread " << std::this_thread::get_id() << "'s i is " << i << strInput;
            std::this_thread::sleep_for(  std::chrono::microseconds(50) );
            std::cout <<  fmts.str() << std::endl;
        }
    }

};



#if 0
int main()
{
    Printer  p;
    // p.Print("hello");


    std::vector<std::thread>  vctThds;

    for(int i = 0; i < 4; i++)
    {
        //std::thread  t1( &Printer::Print,  &p, "thread2" );
        vctThds.emplace_back( &Printer::Print, &p, "");

    }

    for(auto &t : vctThds)
    {
        if(t.joinable())
            t.join();
    }


    /*
    std::thread  t2( &Printer::Print,  &p, "thread3" );
    if(t1.joinable())
        t1.join();
    if(t2.joinable())
        t2.join();
    */

    
    return 0;
}
#endif