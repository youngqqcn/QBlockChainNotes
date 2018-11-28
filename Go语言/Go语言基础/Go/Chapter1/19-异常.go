package main

import (
	"errors"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/11/28  16:21
*描述:
	go语言异常机制
	
	1.error    通常, 函数的最后一个返回值, 用来返回错误信息
	2.panic 和 recover


*/

func TestError(a , b  float64 ) (result float64, err error)  {
	if b == 0{
		result = 0.0
		err = errors.New("divide by zero")
	}else{
		result = a / b
		err = nil
	}
	return
}

func TestPanicA()  {
	fmt.Printf("TestPanicA()")
}

func TestPanicB() (err error)  {

	defer func() {
		if x := recover(); x != nil{
			err = fmt.Errorf("internal error: %v", x)
		}
	}()

	//defer func() {
	//	panic("defer panic")  //这个panic被捕获 , 即: 如果延迟函数中发生panic,
	                          ////能被后续的延迟函数捕获, 但只能捕获到最后一个
	//}()

	panic("func TestPanicB() panic") //这个panic捕获不到了
	//return  err  //可有可无
}

func TestPanicC()  {
	fmt.Printf("TestPanicC()")
}


func main() {

	{
		result, err := TestError(9, 0)
		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(result)
	}
	fmt.Println("==========================")

	{
		result, err := TestError(9, 4)

		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(result)
	}

	/////////////////////////////////////////

	TestPanicA()
	err := TestPanicB()
	if err != nil{
		fmt.Println(err.Error())
	}
	TestPanicC()
}
