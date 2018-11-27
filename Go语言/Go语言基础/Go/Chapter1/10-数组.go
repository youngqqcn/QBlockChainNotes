package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/27  20:27
*描述: 数组
*/

func ModifyArr(intArr [10]int) /*值传递*/  {
	intArr[0] = 999
}

func ModifyArrByPointer( pIntArr *[10]int) /*地址传递*/  {
	(*pIntArr)[0] = 999
}

func Print2DArray( int2DArr [10][10]int)   {
	for i := 0; i < 10; i++{
		for j := 0; j < 10; j++{
			int2DArr[i][j] = i * j
			fmt.Printf("%d\t", int2DArr[i][j])
		}
		fmt.Println("")
	}

}

func Print2DArrayPlus( int2DArr [10][10]int)  {
	for i, arr := range int2DArr{//第一个是元素下标,第二个是元素的值
		for j, _:= range arr{
			fmt.Printf("%d\t", i * j)
		}
		fmt.Println("")
	}
}

func main() {

	var intArr   [10]int
	for i := 0; i < 10; i++{
		intArr[i] = i
	}

	fmt.Println("修改前:", intArr)
	ModifyArr(intArr)
	fmt.Println("修改后:", intArr)
	fmt.Println("==================================")
	fmt.Println("修改前:", intArr)
	ModifyArrByPointer(&intArr)
	fmt.Println("修改后:", intArr)
	fmt.Println("==================================")
	/////////////////////////////////

	var arr2D  [10][10]int
	Print2DArray(arr2D)
	fmt.Println("==================================")

	//////////////////////////////////
	Print2DArrayPlus(arr2D)
	fmt.Println("==================================")

}
