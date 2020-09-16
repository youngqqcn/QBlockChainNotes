#include <iostream>
#include <stdio.h>

constexpr int fibonacci(const int n)
{
    //std::cout << n << std::endl;
    printf("%d\n", n);
    //return (1 == n || 2 == n) ? 1 : (fibonacii(n - 1) + fibonacii(n - 2));
    if(n == 1) return 1;
    if(n == 2) return 1;
    return fibonacci(n-1) + fibonacci(n-2);
}


int main(int argc, const char** argv) 
{
    int a[fibonacci(5)] = { 0 };
    int b[fibonacci(5)] = { 0 };
    return 0;
}