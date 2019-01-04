package main

import (
	"runtime"
	"sync"
	"fmt"
)


//运行结果是?

func main() {
	runtime.GOMAXPROCS(1)
	wg := sync.WaitGroup{}
	wg.Add(20)
	for i := 0; i < 10; i++ {
		go func() {
			fmt.Println("A: ", i)
			wg.Done()
		}()
	}
	for i := 0; i < 10; i++ {
		go func(i int) {
			fmt.Println("B: ", i)
			wg.Done()
		}(i)
	}
	fmt.Println("hello")
	wg.Wait()
}




































/*

func main() {
	runtime.GOMAXPROCS(1) //设置同一时间只能运行一个协程
	wg := sync.WaitGroup{}
	wg.Add(20)
	for i := 0; i < 10; i++ {
		go func() {
			fmt.Println("A: ", i, ", &i=", &i)
			wg.Done()
		}()
		time.Sleep(1000)
	}
	for i := 0; i < 10; i++ {
		go func(i int) {
			fmt.Println("B: ", i, ", &i=", &i)
			wg.Done()
		}(i)
	}
	wg.Wait()
}

*/
