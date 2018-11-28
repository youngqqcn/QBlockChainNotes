package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/28  10:36
*描述:  讨论方法集问题

	关于方法集总结:
`		+--------------------+-----------------------------------+
		| 接收者              | 方法集							  |
		+--------------------+-----------------------------------+
		|   T 				  |  func (t T)                      |
		+--------------------+-----------------------------------+
		|  *T                |  func (t T)  and  func (t *T)     |
		+--------------------------------------------------------+

	自定义类型  编译会自动转换

	接口类型    不能转换, 即  如果一个方法的接收者是 *T ,
				那么必须使用 *T调用, 不能用 T调用
			  因为,  T的方法集是  *T的方法集的  子集

*/

type TestInterface interface{
	SetNameByValue( string)   //值作为接收者
	SetNameByPointer( string) //地址为接收者
}


type Stu struct {
	strName string
}

//值作为接收者
func (stu Stu)SetNameByValue( strName string)  {
	stu.strName = strName
}

//指针作为接收者
func (pStu *Stu)SetNameByPointer( strName string)  {
	pStu.strName = strName
}

func main() {

	stu := Stu{"yqq"}

	stu.SetNameByValue("stu.SetNameByValue") //值传递
	fmt.Println(stu.strName)
	fmt.Println("=====================")

	stu.SetNameByPointer("stu.SetNameByPointer")//编译器会自动 将 T 转为 *T
	fmt.Println(stu.strName)
	fmt.Println("======================")


	(&stu).SetNameByPointer("(&stu).SetNameByPointer")//常规操作
	fmt.Println(stu.strName)
	fmt.Println("======================")

	/////////////////////////////
	var testInterface TestInterface
	testInterface = &stu
	testInterface.SetNameByPointer("usa")
	fmt.Println(stu.strName)
	testInterface.SetNameByValue("france")
	fmt.Println(stu.strName)


	stu2 := Stu{"Messi"}
	var testInterface2 TestInterface

	//testInterface2 = stu2      //错误 , SetNameByPointer method has pointer receiver,
								//必须使用 *T

	testInterface2 = &stu2  // 正确


	testInterface2.SetNameByValue("haha")



}
