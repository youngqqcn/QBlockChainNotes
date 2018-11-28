package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/28  9:13
*描述: 结构体

	匿名字段
	同名字段(即与匿名字段中的变量重名, 如果需要使用, 须显示调用)
	结构体做函数参数 (值传递)
	结构体指针做函数参数(地址传递)

*/

type Person struct {
	strName string  //作者姓名
	intAge int   //作者年龄
}

type Publisher struct {
	strName string
	intId  int
}

type   Book struct{
	Publisher  //出版社信息    匿名字段
	person Person  //作者的信息
	strName string
	floatPrice  float32
}


//写一个简单双向链表
type Node struct {
	value int
	pNext *Node
	pFront *Node
}



func main() {

	var  book Book = Book{
		Publisher{"某宝出版社", 666},
	Person{"青青斯基", 23},
	"go语言学习笔记", 36.6}


	fmt.Println(book)
	fmt.Printf("%d\n", book.person.intAge)
	fmt.Printf("%d\n", book.intId)
	fmt.Printf("%d\n", book.Publisher.intId) //和 book.intId等价

	///////////////////////////////////////

	//简单双向循环链表
	headNode := Node{-1, nil, nil}
	pCurNode := &headNode
	for i := 0; i < 10; i++{
		pCurNode.pNext = new(Node)
		pCurNode.pNext.pNext = nil
		pCurNode.pNext.pFront = pCurNode
		pCurNode.pNext.value = i

		pCurNode = pCurNode.pNext  //指向下一个节点
	}
	pCurNode.pNext = &headNode
	headNode.pFront = pCurNode

	//顺序打印双向循环链表
	for node := headNode; ; node = *(node.pNext){
		fmt.Printf("%d ", node.value)
		if *node.pNext == headNode{
			break
		}
	}
	fmt.Println("")

	//逆序打印双向循环链表
	for node := *(headNode.pFront); ; node = *(node.pFront){
		fmt.Printf("%d ", node.value)
		if node.pFront == headNode.pFront{
			break
		}
	}
	fmt.Println("")

	///////////////////////////////////

	publisher := Publisher{"x", -9}
	ModifyStructInfo(publisher)
	fmt.Println(publisher)
	ModifyStructInfoByPointer(&publisher)
	fmt.Println(publisher)

}

//值传递
func ModifyStructInfo(publisher Publisher) {
	publisher.strName = "yqq"
	publisher.intId = 999999
}

//地址传递
func ModifyStructInfoByPointer(publisher *Publisher) {
	publisher.strName = "yqq"
	publisher.intId = 999999
}
