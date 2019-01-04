package main

import "fmt"


/*

recover函数会使程序从panic中恢复

 */


func defer_call3()  {
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
	defer func(){
		if err := recover(); err != nil{
			fmt.Println(err)
		}

		defer_call3()
	}()
	defer func() {fmt.Println("mainD")}()
	defer func() {fmt.Println("mainE")}()
	defer func() {fmt.Println("mainF")}()

}







































/*
我的答案: C B A  panic:发生异常  mainC mainB mainA  程序中断
正确答案: mainF mainE mainD C B A   mainC mainB mainA    panic:发生异常    程序中断


理解:
 	1.panic会向上传递, 直到defer栈为空时, panic才会中断程序
	2.recover必须在  defer函数中使用, 目的是, 当panic时, 遇到recover会恢复

 */
