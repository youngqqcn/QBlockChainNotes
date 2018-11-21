package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/21  19:06
*描述: 分析go语言中  匿名函数捕获变量的特点
*/

func Sqrt() func() int  {  //返回值为一个   fun() int   函数
	var x int

	return func() int { //返回一个匿名函数
		x ++
		return  x * x
	}
}

func main() {

	var x int = 9
	funcTmp := Sqrt()
	fmt.Println(funcTmp()) //1
	fmt.Println(funcTmp()) //4
	fmt.Println(funcTmp()) //9
	fmt.Println(funcTmp()) //16
	fmt.Println("============\n","x=", x)


	//我们看到变量的生命周期不由它的作用域决定：
	//       squares返回后，变量x仍然隐式的存在于funcTmp中
    // 我的理解:
    //      funcTmp拥有自己的一片栈空间, funcTmp在main是是一个函数变量,
    //      在main函数结束前, funcTmp一直有效, 而 x是funcTmp栈空间中的一个变量
    //      既然, funcTmp的栈空间未被清掉,  那么 x 自然就存在....
    //
    //    所以, 从内存空间上看这个问题, 就很容易理解了
}
