package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/21  17:54
*描述: 常量

在一个const声明语句中，在第一个声明的常量所在的行，
iota将会被置为0(遇到一个新的const关键字, 就会重置)，
然后在每一个有常量声明的行 会自动加1
*/

const (
	constX = iota     //iota 是常量生成器
	constY = iota     // constY 是 1
	Z   //默认是  Z=iota,  这里是  Z是 2
)

func main() {

	fmt.Println(constX)
	fmt.Println(constY)
	fmt.Println(Z)

	///////////////////////////////////////
	const (
		a, b, _, c = iota, 999, iota, "战争与和平"
	)

	fmt.Println(a)
	//b = 9   //常量不能被修改
	fmt.Println(b)
	fmt.Println(c)


	/////////////////////////////////////
	const (
	x1 = iota * 10  //0
	x2 = iota * 10  //10
	x3 = iota * 10  //30
	)
	fmt.Println(x1)
	fmt.Println(x2)
	fmt.Println(x3)
}
