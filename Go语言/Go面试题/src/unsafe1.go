package main

import (
	"unsafe"
	"fmt"
)

/**
*作者: yqq
*日期: 2019/1/7  23:34
*描述:



*/


func main() {


	//var x := nil
	//fmt.Println(x)

	a := "hello543509348503458340534593490543905"
	fmt.Println(a[4:])
	fmt.Println(len(a))
	fmt.Println(	 unsafe.Sizeof(a) )



	s := make([]int, 10, 11)
	fmt.Println(len(s))
	fmt.Println(cap(s))


}
