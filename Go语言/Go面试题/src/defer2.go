package main

/*

recover函数会使程序从panic中恢复

 */

import "fmt"

func defer_call2()  {

	defer func() {
		if  err := recover(); err != nil{
			fmt.Println(err)
		}
	}()

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
	defer_call2()
	defer func() {fmt.Println("mainD")}()
	defer func() {fmt.Println("mainE")}()
	defer func() {fmt.Println("mainF")}()

}








































/*
我的答案:  C B A 发生异常 F E D  mainF mainE mainD mainC mainB mainA
正确答案:  C B A 发生异常 F E D  mainF mainE mainD mainC mainB mainA
 */