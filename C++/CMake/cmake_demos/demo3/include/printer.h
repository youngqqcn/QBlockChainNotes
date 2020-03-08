#pragma once

#include <iostream>


template < typename T>
static void Print(const T &input) noexcept(false)
{
    std::cout << input << std::endl;
}


struct CPrinter
{
    void Show();

    int a = 0;
    int b = 0;
};