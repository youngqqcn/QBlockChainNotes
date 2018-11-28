package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/28  20:56
*描述:  生产者-消费者模型  go语言实现
*/

func producer(chProducts chan int)  {
	defer close(chProducts)
	for i := 0; i < 10; i++{
		fmt.Printf("puts product %d\n", i)
		chProducts <- i
	}
}

func consumer(chProducts chan int)  {

	//i := 0
	for {
		//select {
		//case  value := <- chProducts:
		//	i++
		//	fmt.Printf("get product %d\n", value)
		//	if i >= 10{
		//		return
		//	}
		//default:
		//	continue
		//}



		if  value, ok := <- chProducts; ok{
			fmt.Printf("get product %d\n", value)
		}else{
			fmt.Println("通道已关闭")
			return
		}
	}

}

func main() {

	chProducts := make(chan int)
	go producer(chProducts)
	consumer(chProducts)

}
