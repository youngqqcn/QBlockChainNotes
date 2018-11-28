package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/28  15:48
*描述:
	关于类型断言的总结

	断言类型的语法：
			x.(T)，这里x表示一个接口的类型，T表示一个类型（也可为接口类型）。

	第一种情况:  T是一个具体的类型(包括基本类型, 结构体, 函数...)

	第二种情况: T是一个接口类型, ok的话则会进行类型转换


参考:
https://www.cnblogs.com/susufufu/archive/2017/08/13/7353290.html
*/

type TestInterface1 interface {
	getName() string
}

type TestInterface2 interface {
	printName()
}

type Vip struct {
	name string
}

func (pVip Vip)getName() string  {
	return pVip.name
}

func (vip Vip)printName()   {
	fmt.Println(vip.name)
}


func main() {

	vip := Vip{"yqq"}
	//vip.printName()

	var tester TestInterface1
	tester = vip

	//第一种 : x.(T)  T是一个具体类型, 仅检查类型是否匹配
	if obj , ok := tester.(Vip); ok{
		fmt.Printf("%T  %s\n", obj, obj.getName())
	}

	//第二种:  x.(T)   T是一个接口类型, 则会进行类型转换
	if obj, ok := tester.(TestInterface2); ok{
		obj.printName()
	}

}
