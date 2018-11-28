package main

import (
	"fmt"
	"time"
)

/**
*作者: yqq
*日期: 2018/11/28  17:17
*描述:  go语言并发




*/



/*
func2只打印2两次, 因为   ch<-999 阻塞了,  
main gorutine中只从ch中接收了一次
 */
func Test1()  {

	ch := make(chan int)
	go func() {
		for ;;{
			//runtime.Gosched()
			fmt.Println("func1")
			time.Sleep(1 * time.Second)
		}
	}()

	go func() {
		for ;; {
			fmt.Println("func2")
			time.Sleep(1* time.Second)
			//runtime.Gosched()

			ch <- 999
		}
	}()

	retValue := <-ch
	fmt.Println(retValue)

	time.Sleep(3 *time.Second)
}

func Test2()  {

	ch := make(chan string, 10)
	go func() {
		for ;;{
			fmt.Println("A")
			time.Sleep(1 * time.Second)
			ch <- "haha"
		}
	}()

	go func() {
		for ;;{
			fmt.Println("B")
			time.Sleep(2 * time.Second)
			<- ch
		}
	}()

	time.Sleep(5 * time.Second)

}

func Test3()  {

	ch := make(chan int, 10)

	go func() {
		for i := 0; i <10; i ++{
			ch <- i  //往通道发送数据
		}
		close(ch)  //close 注释掉, 会导致死锁
	}()

	for data := range ch{
		fmt.Println(data)
	}
}

func Test4()  {

	ch := make(chan int)
	timer := time.NewTimer(3 * time.Second)
	go func() {
		<- timer.C
		fmt.Println("3s已过")
		ch <- 1
	}()

	<-ch

	if isStop := timer.Stop(); isStop{
		fmt.Println("已停止")
	}
}

func fib(ch, quit chan int) {

	x, y := 1, 1

	for {
		select {
		case ch <- x:
			x , y = y, x + y
		case <-quit:
			fmt.Println("quit")
			return
		//default:
		//	fmt.Println(".")
		}
	}
}


func SetTimer(ch, quit chan int){

	for{
		select {
		case v  := <- ch:
			fmt.Println(v)
		case <-time.After(5 * time.Second):  //超时设置
			fmt.Println("timeout")
			quit <- 1
			return
		}
	}

}

func SetTicker(quit chan int)  {

	fmt.Println("====================")

	ticker := time.NewTicker(1 * time.Second)  //每隔 1s 触发一次事件

	i := 0
	for {
		<- ticker.C //等待
		fmt.Println(i)
		i++
		if i == 5{
			ticker.Stop()
			quit <- 0
			break
		}

	}
	
}

func main() {

	//Test1()
	//Test2()
	//Test3()
	//Test4()

	ch, quit := make(chan int), make(chan  int)

	go func(){
		for i := 0; i < 10; i++{
			fmt.Println( <- ch)
		}
		quit <- 0  //必须退出, 否则 , 死锁
	}()

	fib(ch, quit)



	//select 设置超时
	go SetTimer(ch, quit)
	ch <- 9
	<- quit

	//////
	go SetTicker(quit)
	<- quit //阻塞等待 SetTicker 向 quit中写数据


}
