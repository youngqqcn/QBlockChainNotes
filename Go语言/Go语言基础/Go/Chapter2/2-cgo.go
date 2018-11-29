package main

/*
#include <stdio.h>
int test() {
    return 2016;
}
*/
import "C"
import "fmt"

/*
import "C"  之前是 C语言代码,   不能有空格或空行 或其他东西!!


如果gcc是32位的, 而编译环境是64位的, 则会报错,  安装mingw64, 并配置环境变量

 */

func main() {
	fmt.Println(C.test())
}
