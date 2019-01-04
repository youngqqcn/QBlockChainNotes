package main

import (
	"runtime"
	"fmt"
)

func main() {
	runtime.GOMAXPROCS(1)
	int_chan := make(chan int, 1)
	string_chan := make(chan string, 1)
	int_chan <- 1
	string_chan <- "hello"
	select {
	case value := <-int_chan:
		fmt.Println(value)
	case value := <-string_chan:
		panic(value)

	}
}









































/*
1.select 中只要有一个case能return，则立刻执行并返回。
2.当如果同一时间有多个case均能return则伪随机方式抽取任意一个执行并返回。
3.如果没有一个case能return则可以执行"default"块。
 */