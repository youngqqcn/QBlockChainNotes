package main

import (
	"math/rand"
	"fmt"
	"time"
)

/**
*作者: yqq
*日期: 2018/11/21  18:04
*描述:
	if ...
	if...else
	if....else if ...else
*/



func main() {

	//用unix时间戳初始化 rand
	rand.Seed(time.Now().UnixNano())

	for i := 0; i < 10; i++{
		fmt.Println(rand.Int())
	}

	if  a := rand.Int() ; (a & 1)==1/*奇数*/{
		fmt.Println(a)
		fmt.Println("奇数")
	}else{
		fmt.Println("偶数")
	}

	//switch语句
	switch rand.Int() % 3{
	case 0:
		fmt.Println(0)
	case 1:
		fmt.Println(1)
	case 2:
		fmt.Println(2)
	}

	switch a := rand.Int() & 1; a {
	case 0:
		fmt.Println("偶数")
	case 1:
		fmt.Println("奇数")

	}

}
