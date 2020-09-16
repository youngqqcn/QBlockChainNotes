//yqq

#include <iostream>
#include <algorithm>
#include <variant>
#include <valarray>
#include <iomanip>

using namespace std;



union MyUnion
{
    int i;
    float f;
    // std::string  str;
    char ch;
};


// 使用 std::variant 实现函数返回多个不同类型的值

using Two = std::pair<double, double>;
//using Roots = std::variant<Two, double, void*>;
// using Roots = std::variant<Two, double, void *>;
using Roots = std::variant<Two, double>;

Roots FindRoots(double a, double b, double c)
{
    auto d = b*b-4*a*c;

    if (d > 0.0)
    {
        auto p = sqrt(d);
        return std::make_pair((-b + p) / 2 * a, (-b - p) / 2 * a);
    }
    else if (d == 0.0)
        return (-1*b)/(2*a);
    // return nullptr;
    return 0.0;
}

struct RootPrinterVisitor
{
    void operator()(const Two& roots) const
    {
        std::cout << "2 roots: " << roots.first << " " << roots.second << '\n';
    }
    void operator()(double root) const
    {
        std::cout << "1 root: " << root << '\n';
    }
    void operator()(void *) const
    {
        std::cout << "No real roots found.\n";
    }
};



int main()
{
    double pi = 3.14159265359;
    const int nSize = 10;
    std::valarray<double>  vctFloats(nSize);
    for(int i = 0; i < nSize; i++)
    {
        vctFloats[i] = 0.25 * i - 1;
    }

    for(int i = 0; i < nSize; i++)
    {
        std::cout << " " << vctFloats[i];
    }
    std::cout << std::endl;



    std::valarray<double> vctFloats2(nSize);
    // vctFloats2 = sin(vctFloats);
    vctFloats2 = acos(vctFloats);

    for (int i = 0 ; i < nSize ; i++ )
    {
      cout << setw(10) << vctFloats2 [ i ]
         << "  radians, which is  "
         << setw(11) << (180/pi) * vctFloats2 [ i ]
         << "  degrees" << endl;
    }


    std::variant<int, float, std::string>  var;
    var =  std::string("hello");
    std::cout << std::get<std::string>(var) << std::endl;  // C++17

    var = (float)0.9999;
    std::cout << std::get<float>(var) << std::endl;


    var = (int) 999;
    std::cout << std::get<int>(var) << std::endl;
    // std::cout << std::get<float>(var) << std::endl; // error
    // std::cout << std::get<std::string>(var) << std::endl;  // error


    // MyUnion  u =  {std::string("string")};
    MyUnion u;
    std::cout << "sizeof(MyUnion) = " << sizeof(MyUnion) << std::endl;
    u.f = 999.999;
    std::cout << u.f << std::endl;
    u.i = 999;
    std::cout << u.i << std::endl;
    // u.str = std::string("hello");
    // std::cout << u.str << std::endl;
    u.ch = 'z';
    std::cout << u.ch << std::endl;
    std::cout << u.f<< std::endl;
    std::cout << u.i<< std::endl;


    // std::visit(RootPrinterVisitor(), FindRoots(1, -2, 1)); // ok
    /*
    std::visit( [&](auto&& x){
        if(std::holds_alternative<Two>(x))
        {
            std::cout << "two roots: " << x.first << ", " << x.second << std::endl;
        }
        else if(std::holds_alternative<double>(x))
        {
            std::cout << "one root: " << x << std::endl;
        }
        // else if(std::holds_alternative<void *&>(x))
        // {
        //     std::cout << "no root" << std::endl;
        // }
        else
        {
            std::cout << "error type" << std::endl;
        }
    }, FindRoots(1, -2, 1));
    */



    return 0;
}
