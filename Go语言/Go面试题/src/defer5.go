package main

import "fmt"

func defer_call5()  {
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
		defer func() {
			if err := recover(); err != nil {
				fmt.Println(err)
			}
		}()

		defer func() {
			panic("panic了")
		}()

		defer_call5()
	}()
	defer func() {fmt.Println("mainD")}()
	defer func() {fmt.Println("mainE")}()
	defer func() {fmt.Println("mainF")}()

}



































/*
我的答案: C B A panic了 mainF mainE mainD mainC mainB mainA
正确答案: mainF mainE mainD C B A panic了 mainC mainB mainA
 */