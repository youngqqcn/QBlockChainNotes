package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/27  19:33
*描述: go语言指针

其他注意:
		与C/C++不同的是, 在Go语言中, 无论是new出来的变量还是局部变量,
       它分配在堆上还是在栈上, 由编译器进行逃逸分析(即是否被返回或者其他地方引用)之后决定的.

*/

type Employee struct {
	id int
	name string
	age byte
	addr  string
}

//指针作为函数参数
func ModifyAddrByPointer(pAddr *string, strNew string)  {
	*pAddr = strNew
}
func ModifyAddrByValue(strAddr string, strNew string)  {
	strAddr = strNew
}

//指针做返回值
func MyMalloc(nSize int) *[]int  {
	intArr := make([]int, nSize)   //intArr 是一个  []int
	fmt.Printf("intArr : %T\n", intArr)
	return &intArr  //返回局部变量的地址
					//特别注意:
					//     这和C语言不同, Go语言编译器会做"逃逸分析(escape analysis)"
					//     来决定局部变量分配在栈上还是堆上, 所以在Go语言中,
					//     这样的做法是没问题的
}


func main() {
	var pEmp  *Employee
	pEmp = &Employee{1, "yqq", 23, "湖南"}

	fmt.Println(pEmp.id)
	fmt.Println(pEmp.name)
	fmt.Println(pEmp.age)
	fmt.Println(pEmp.addr)
	/////////////////////////////
	fmt.Println("=============")
	pEmp2 := &Employee{id:2, name:"qqy", age:23, addr:"China"}
	fmt.Println(pEmp2.id)
	fmt.Println(pEmp2.name)
	fmt.Println(pEmp2.age)
	fmt.Println(pEmp2.addr)

	//////////////////////////////
	fmt.Println("===================")
	var pEmp3 *Employee
	pEmp3 = new(Employee)  //分配空间
	pEmp3.id = 9
	pEmp3.name = "qyq"
	pEmp3.addr = "湖南永州"
	pEmp3.age = 23
	fmt.Println(pEmp3.id)
	fmt.Println((*pEmp3).name) // (*pEmp3).name 和 pEmp3.name等价
	fmt.Println(pEmp3.age)
	fmt.Println(pEmp3.addr)

	///////////////////////////////
	fmt.Println("=======================")
	var Emp1 = Employee{addr:"中国-湖南-永州"}
	ModifyAddrByValue(Emp1.addr, "深圳")   //值传递
	fmt.Println(Emp1.addr) //打印修改后的值

	var Emp2 = Employee{addr:"中国-湖南-永州"}
	ModifyAddrByPointer(&Emp2.addr, "深圳") //地址传递
	fmt.Println(Emp2.addr) //打印修改后的值

	////////////////////////////
	nSize := 10
	pArr := MyMalloc(nSize) //分配10个int
	for i := 0; i < nSize; i++{
		(*pArr)[i] = i * 10
		fmt.Println((*pArr)[i])
	}

}
