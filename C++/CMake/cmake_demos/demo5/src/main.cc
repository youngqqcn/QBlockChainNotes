#include <iostream>

#include "printer.h"


using namespace std;


int main()
{

    CPrinter  prt;
    prt.a = 999;
    prt.b = 444;

    prt.Show();

    std::cout << "hello" << std::endl;


    return 0;
}