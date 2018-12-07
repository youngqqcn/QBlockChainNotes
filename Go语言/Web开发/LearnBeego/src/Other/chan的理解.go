
package main

import (
	"fmt"
	"time"
)

/**
*作者: yqq
*日期: 2018/12/7  14:39
*描述: 理解  make(chan int)  和 make(chan int, 1)  区别
*/




func main() {
	var c = make(chan int, 1)
	var a string

	go func() {
		c <- 0
		time.Sleep(time.Second)
		a = "hello world"
	}()

	<-c
	fmt.Println(a)
}

//func main() {
//	var c = make(chan int, 1)
//	var a string
//
//	go func() {
//		a = "hello world"
//		c <- 0
//	}()
//
//	 <-c
//	fmt.Println(a)
//}
/*
可能输出 hello world
 */


//func main() {
//	var c = make(chan int, 1)
//	var a string
//
//	go func() {
//		a = "hello world"
//		<-c
//	}()
//
//	c <- 0
//	fmt.Println(a)
//}
/*
可能输出 hello world, 也可能输出为空(子goroutine快于main goroutine)
 */



//func main() {
//	var c = make(chan int)
//	var a string
//
//	go func() {
//		a = "hello world"
//		<-c
//	}()
//
//	c <- 0
//	fmt.Println(a)
//}
/*
输出    hello world
 */

