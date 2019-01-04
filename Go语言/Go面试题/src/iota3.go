package main

import "fmt"

/**
*作者: yqq
*日期: 2019/1/4  12:37
*描述:
*/


const (
	i = iota
	j
)

//k = iota //error
const l = iota

const (
	v = iota
	m = "hello"
	n
	o = iota
)






func main() {

	fmt.Println(i, j, l, v, m, n, o)

}














































//iota 只能修饰const常量
//每遇到一个const,  iota就会重置为0
//在golang中, 如果
