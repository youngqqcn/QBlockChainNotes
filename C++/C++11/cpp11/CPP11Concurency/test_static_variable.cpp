#include <iostream>

int  foo()
{
    static int n_number = 0;
    return n_number ++;
}

#if 0

int main()
{
    std::cout << foo() << std::endl;
    std::cout << foo() << std::endl;
    std::cout << foo() << std::endl;
    std::cout << foo() << std::endl;


    return 0;
}
#endif