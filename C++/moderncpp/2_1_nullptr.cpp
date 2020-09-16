#include <iostream>
#include <type_traits>

void foo(char *) {
    std::cout << "foo(char*) is called" << std::endl;
}
void foo(int i) {
    std::cout << "foo(int) is called" << std::endl;
}


constexpr int fibonacii(const int n)
{
    std::cout << n << std::endl;
    return (1 == n || 2 == n) ? 1 : (fibonacii(n - 1) + fibonacii(n - 2));
}

int main(int argc, const char** argv) 
{
    if(std::is_same<decltype(NULL), decltype(0)>::value)
    {
        std::cout << "NULL == 0" << std::endl;
    }
    if (std::is_same<decltype(NULL), decltype((void*)0)>::value)
        std::cout << "NULL == (void *)0" << std::endl;
    if (std::is_same<decltype(NULL), std::nullptr_t>::value)
        std::cout << "NULL == nullptr" << std::endl;

    foo(0);
    // foo(NULL);  //编译失败
    foo(nullptr);


    // std::cout << fibonacii(5) << std::endl;
    int a[fibonacii(5)] = {0};

    return 0;
}