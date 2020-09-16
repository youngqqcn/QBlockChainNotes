//yqq

#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;


typedef int(*cbfunc)(int, int); //回调函数类型
using cbfuncex = int(*)(int, int);

using VCTINT = std::vector<int>;

int foo(int a, int b)
{
    return a + b;
}

void run( cbfunc func , int a, int b)
{
    std::cout << func(a, b) << std::endl;
}

int main()
{
    cbfunc  cb = foo;
    run(cb, 9, 10);

    cbfuncex cbex = foo;
    run(cbex, 10, 29);

    VCTINT a = {9, 2, 39, 10};
    for_each(a.begin(), a.end(), [](int n){
        std::cout << n << std::endl;
    });

    return 0;
}
