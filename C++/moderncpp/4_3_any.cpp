//yqq

#include <iostream>
#include <algorithm>
#include <any>  //c++17
#include <string>

using namespace std;


int main()
{

    std::any  a = 9;
    std::cout << std::any_cast<int>(a) << std::endl;

    a  = std::string("this is a");
    std::cout << std::any_cast<std::string>(a) << std::endl;


    a.reset(); //删除a 中的值
    if( a.has_value())
    {
        std::cout << "a 中有值" << std::endl;
    }
    else
    {
        std::cout << "a 中无值" << std::endl;
    }
    


    return 0;
}
