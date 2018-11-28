package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/28  13:32
*描述: 空接口

	空接口的用途
		1.存储任意类型
		2.作为函数参数, 实现不定参数


	关于类型断言:  x.(T)
		第一种: 当T是一个具体的类型时, x.(T)的作用 仅仅是检查x的类型是否是 T
				例如: value, ok := strTest.(string)   ok为true
		             value, ok := intAge.(string)   ok为false

		第二种:  当T是一个接口类型时, x.(T)的作用是, 检查x是否满足T接口
				如果检查成功:  则 x 被转换成 T接口类型
				如果检查失败:  抛panic, 除非用两个值接受


*/

func test()  {
	fmt.Println("hello")
}

func ShowType( a interface{})  {
	switch a.(type) {
	case string:
		fmt.Println("string")
	case int:
		fmt.Println("int")
	case map[interface{}]interface{}:
		fmt.Println("map")
	case func():
		fmt.Println("func")
	/*case interface{}:
		fmt.Println("interface")
	case []interface{}:
		fmt.Println("[]interface{}")*/
	default:
		fmt.Printf("%T\n", a)

	}
}

func ShowType2(a interface{}){
	 if _,  ok := a.(string); ok{
	 	fmt.Println("string")
	 }else if _, ok := a.(int); ok{
		 fmt.Println("int")
	 }else if _, ok := a.(func()) ; ok{
	 	fmt.Println("func")
	 }else if _, ok := a.(interface{}); ok{
	 	fmt.Println("interface{}")
	 }
}

//不定参数(类型确定, 参数个数不确定)
func MyPrintln(args ...int)  {
	for i, arg := range args{
		fmt.Printf("args[%d]=%d\n", i, arg)
	}
}

//不定参数(类型 和 参数个数都不确定)
func MyPrintlnPlus(args ...interface{})  {
	for i, _ := range args{
		switch args[i].(type) {
		case int:
			fmt.Printf("int  %d\n", args[i])
		case string:
			fmt.Printf("string %s\n", args[i])
		case map[int]string:

			/*
			for k, v := range args[i]{ //错误
				fmt.Printf("map[%v]=%v", k, v)
			}
			*/
			a, b := args[i].(int)
			fmt.Printf("a=%v\n", a)
			fmt.Printf("b=%v\n", b)

			// 如果 args[i].(map[int]string)断言成功, 则
			// 将interface{} 转为 map[int]string类型
			// 否则, 会抛出panic
			for k, v := range args[i].(map[int]string){ //一旦类型不匹配, 就panic
				fmt.Printf("map[%v]=%v\n", k, v)
			}

			//以下是正确的写法
			if  m , ok := args[i].(map[int]string); ok{
				for k, v := range m{
					fmt.Printf("map[%v]=%v\n", k , v)
				}
			}
		default:
			fmt.Println("unknow")
		}
	}
}




func main() {

	var slice  [3]interface{}   //数组

	slice[0] = "hello"
	slice[1] = test
	slice[2] = [3]interface{}{"你好", 99.9, test}

	fmt.Println(slice)

	for i, v := range slice{
		fmt.Printf("slice[%d]=%v\n", i, v)
	}
	fmt.Println("======================")
	ShowType(slice[0])
	ShowType(slice[1])
	ShowType(slice[2])
	////////////////////////////////
	fmt.Println("=======================")

	ShowType2(slice[0])
	ShowType2(slice[1])
	ShowType2(slice[2])

	fmt.Println("============================")

	MyPrintln(1, 2, 99, 2, 33, 4, 88, 923)
	fmt.Println("============================")
	MyPrintlnPlus("你好", 99, map[int]string{1:"哈哈"})


}
