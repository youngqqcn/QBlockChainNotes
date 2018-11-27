package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/27  20:47
*描述: 切片

注意:  切片只是一个引用类型 (和C++或Java中的引用类型类似 但是  又不同)
      不同的是  Go语言的切片类型可以改变 "指向", 即 切片与底层数组的关系 会被改变.

切片和数组的区别

数组声明时需要指定长度或者使用 ... 自动计算长度
切片不需要指定长度

*/



func main() {

	//var  arr [10]int  //声明数组
	//var  slice []int  //切片
	//var  slice1 []int = []int{1, 2, 3}  //切片
	//var slice2 []int = make([]int, 10/*长度*/, 10/*容量*/) //切片
	//slice3 := make([]int , 10, 10) //切片

	intArr := [...]int{1, 3, 34, 23, 3, 5, 9, 10, 11, 99, 27, 86, 84}
	slice := intArr[:]

	PrintSlice(slice)

	fmt.Println("=========================")
	ModifySlice(slice)
	PrintSlice(slice)
	fmt.Println("=========================")
	fmt.Printf("切片做参数(值传递)\n")
	MyAppend(slice)
	PrintSlice(slice)
	fmt.Println(intArr)

	slice[0] = 77777
	fmt.Println(slice)
	fmt.Println(intArr)
	fmt.Println("=========================")

	fmt.Printf("切片指针做参数....\n")
	MyAppendPlus(&slice)
	PrintSlice(slice)
	fmt.Println(intArr)

	//切片和原来的底层数组的映射关系 被 MyAppendPlus破坏了
	// 即 slice不再指向intArr
	slice[0] =  88888
	fmt.Println(slice)
	fmt.Println(intArr)

}

func PrintSlice(slice []int)  {
	for i, value := range slice{
		fmt.Printf("s[%d]=%d\n", i, value)
	}
}

func ModifySlice(slice []int)  {

	for i, value := range(slice){
		slice[i] = value * 100
	}

}

func MyAppend(slice []int)  {
	slice = append(slice, 5555, 5555, 5555, 5555)
}

func MyAppendPlus(pSlice *[]int /*切片指针*/)  {
	*pSlice = append(*pSlice, 5555, 5555, 5555)
}


