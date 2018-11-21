package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/21  18:36
*描述: 函数

	函数名
		首字母小写   private (只能在本文件中用)
        首字母大写   public  (其他文件可以用)
*/

type FuncType func(int, int, string) int //声明函数类型

func Sum(a, b int, strInfo string) int {
	fmt.Println(strInfo)
	return  a + b
}

func main() {

	MySum := Sum
	fmt.Println(MySum(99, 90, "99, 90"))

	var MySum2 FuncType = Sum
	fmt.Println(MySum2(22, 33, "22, 33"))

	/////////////////////////
	//匿名函数
	fmt.Println("0+1+2+...+100=", func() int{
		sum := 0
		for i := 0; i <= 100; i++{
			sum += i
		}
		return  sum
	}())


	//带参数   有返回值
	tmpFunc := func(a, b int) (ret int){
		ret = a + b
		return ret
	}(1, 9)
	fmt.Println(tmpFunc)

	///////////////////////////////




}
