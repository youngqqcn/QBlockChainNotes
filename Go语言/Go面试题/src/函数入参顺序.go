package main

import "fmt"

func TestArgs(a , b, c int)  {

	fmt.Println(a, b, c)

}

func Add(a *int,  v int) int {
	*a += v
	return *a
}

func main()  {

	var a = new(int)
	*a = 10
	//Add(a, 2)
	//fmt.Println(a)
	//fmt.Println(*a)

	TestArgs( Add(a, 2), Add(a, 5), Add(a, 9) )

}




































/*  C/C++


#include<stdio.h>

void TestArgs(int a, int b, int c)
{
    printf("%d  %d   %d", a, b, c);
}

int Add(int *a, int v)
{
    *a += v;
    return *a;
}

int main()
{
    int a = 10;
    int *pa = &a;
    TestArgs(Add(pa, 2), Add(pa, 5), Add(pa, 9));
    return 0;
}

//windows, gcc 输出结果是 26  24   19
//windows, MSVC 输出的是  26  24   19
//ubuntu, g++ 输出  26  24  19

 */










//windows和Ubuntu都是输出:  12 17 26
//结论: golang 入参顺序是 从左向右
//     C/C++ 入参顺序是  从右向左

