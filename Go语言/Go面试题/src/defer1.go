package main

import "fmt"

/**
*作者: yqq
*日期: 2019/1/3  19:13
*描述: defer panic
*/

func defer_call()  {

	defer func() {fmt.Println("A")}()
	defer func() {fmt.Println("B")}()
	defer func() {fmt.Println("C")}()
	panic("发生异常")
	defer func() {fmt.Println("D")}()
	defer func() {fmt.Println("E")}()
	defer func() {fmt.Println("F")}()

}


func main() {

	defer func() {fmt.Println("mainA")}()
	defer func() {fmt.Println("mainB")}()
	defer func() {fmt.Println("mainC")}()
	defer_call()
	defer func() {fmt.Println("mainD")}()
	defer func() {fmt.Println("mainE")}()
	defer func() {fmt.Println("mainF")}()

}



































/*
我的答案: C  B  A  panic("发生异常")
正确答案: C B A panic:发生异常  mainC  mainB  mainA


defer 是FILO

可以理解: 每个函数(每个作用域都有自己的defer函数栈)
发生panic时, 首先执行本函数的defer函数栈, 当本函数的函数栈清空之后, 才会真正触发panic向上传递.


 */
