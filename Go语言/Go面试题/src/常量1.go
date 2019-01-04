
package main

//下面函数有什么问题?
const cl  = 100

var bl    = 123

func main()  {
	println(&bl,bl)
	println(&cl,cl)
}





















































//变量在运行期分配内存，
// 常量在预处理阶段直接展开，作为指令数据使用，



/*

#include <stdio.h>
const int a = 0;
int main()
{
    printf("%p\n", &a);
    return 0;
}

 */