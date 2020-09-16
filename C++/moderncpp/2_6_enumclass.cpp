//yqq

#include <iostream>
#include <algorithm>
#include <string>
using namespace std;



enum class RGB : unsigned int{ 
    RED = 0x0,
    GREEN = 0xff,
    BLUE = 0xffff,
};

enum class  HHH { 
    RED = 0x0,
    GREEN = 0xff,
    BLUE = 0xffff,
};

enum class MAP : int {
    FIRST = -1,
    SECOND = -999,
    THRID  = 19900
};


template<typename T>
std::ostream& operator<< (typename std::enable_if<std::is_enum<T>::value, std::ostream>::type& stream, const T& e)
{
    return stream << static_cast<typename std::underlying_type<T>::type>(e);
}



int main()
{
    // if(RGB::RED == HHH::BLUE) // 编译不过
    if(RGB::RED == RGB::BLUE)
    {
        std::cout << "RGB::RED == RGB::BLUE" << std::endl;
    }
    std::cout << MAP::THRID << std::endl;


    return 0;
}
