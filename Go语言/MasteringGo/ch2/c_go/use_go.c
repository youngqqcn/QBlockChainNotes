#include <stdio.h>
#include "use_by_c.h"


int main()
{
    GoInt x = 99;
    GoInt y = 99;
    printf("call go function\n");
    printf("result is %lld\n", Mul(x, y) );
    PrintMessage();
    return 0;
}