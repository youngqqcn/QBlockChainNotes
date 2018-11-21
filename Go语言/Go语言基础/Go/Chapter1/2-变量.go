package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/21  17:37
*描述: 变量声明, 定义, 赋值, 匿名变量
*/

func Test() (int , string) {
	return  666, "很牛的样子"
}

func main() {

	/////////////////////////////////
	var a int
	a = 9
	fmt.Println( a)

	/////////////////////////////////
	var b string
	b = "hello"
	fmt.Println(b)

	/////////////////////////////////
	var c, d float64
	c , d = 99.3 , 23.3   //分别给 c 和 d 赋值
	fmt.Println("c=", c, "\n", "d=", d)

	/////////////////////////////////
	var (
		e int64
		f float64
	)
	e = 9234230948
	f = 4329482394
	fmt.Println(e)
	fmt.Println(f)
	/////////////////////////////////

	g := "定义一个变量"    //     := 不能用来给已经声明过的变量赋值
	fmt.Println(g)

	/////////////////////////////////
	_, x, _, y := 1, "x", 43.3, 99   // _ 表示匿名变量, 一般用来丢弃没用到的函数的返回值
	fmt.Println(x, "\n", y)

	/////////////////////////////////
	_, desc := Test()   //Test() 的第一个返回值被丢弃
	fmt.Println(desc)
}
