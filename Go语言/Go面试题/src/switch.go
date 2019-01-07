package main

import "fmt"

/**
*作者: yqq
*日期: 2019/1/7  22:01
*描述:

*/



func main() {

	var a = 10
	switch  a  {
	case 10:
		fmt.Println("hello")
		fallthrough
	default:
		fmt.Println("default")

	}

}
