package main

import "fmt"

/**
*作者: yqq
*日期: 2019/1/4  20:04
*描述:


*/




func main() {


	s := []int{1, 2 , 3, 4}

	fmt.Println(s[:]) 		//[1, 2, 3, 4]
	fmt.Println(s[0:4])  	//[1, 2, 3, 4]
	fmt.Println(s[1:3])  	//[2, 3]
	fmt.Println(s[1:4]) 	//[2, 3, 4]
	fmt.Println(s[3]) 		// 4

	fmt.Println(s[0:0]) 	//[]
	fmt.Println(s[4:]) 		//[]                     ???????
	s1  := s[:4] 		//[]                     ???????
	fmt.Println(s1)
	//fmt.Println(s[4]) 	//error
	//fmt.Println(s[5:]) 	//error


	fmt.Println("====================")

	fmt.Println(cap(s))
	fmt.Println(len(s))

}

//解释:  slice的切片操作s[i:j]，其中0 ≤ i≤ j≤ cap(s)
// 当  s[4:]    满足      4<=cap(s)的条件,  但是为空
// python 中也是如此
//
//这个问题很难理解, 先放放
