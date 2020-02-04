#include <functional>
#include <iostream>
#include <string>
#include <map>


int add(int a, int b)
{
    return a + b;
}

int mul(int a, int b)
{
    return a * b;
}



#if 0
int main()
{

    auto fn = std::function<int(int, int)>(add);
    std::map<std::string,  decltype(fn) >  mapFns;

    mapFns.insert( std::make_pair( "+", fn ));
    mapFns.insert( std::make_pair("*", std::function (mul)) );

    mapFns.insert( std::make_pair("-", [](int a, int b) -> int{
        return a - b;
    }) );


    std::cout <<   mapFns["*"](6, 9) << std::endl;  //54
    std::cout <<   mapFns["+"](6, 9) << std::endl;  //15
    std::cout <<   mapFns["-"](6, 9) << std::endl;  //-3

    return 0;
}
#endif