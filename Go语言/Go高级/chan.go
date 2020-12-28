package main

import "fmt"

// func main() {

// 	ch := make(chan int)

// 	for i := 0; i < 10; i++ {
// 		go func(n int, c <-chan int) {
// 			for {
// 				fmt.Printf("goroutine:%v, %v \n", n, <-c)
// 			}
// 		}(i, ch)
// 	}

// 	for i := 0; i < 100; i++ {
// 		ch <- i
// 	}
// 	// select{}
// }

func main() {
	c := make(chan int)

	n := &node{
		ch: make(chan int),
	}

	fmt.Println("&c:", &c)
	fmt.Println("&n:", &n.ch)
	fmt.Println("c:", c)
	fmt.Println("n:", n.ch)
	fmt.Println()

	// 赋值
	c = n.ch
	
	fmt.Println("&c:", &c)
	fmt.Println("&n:", &n.ch)
	fmt.Println("c:", c)
	fmt.Println("n:", n.ch)
	fmt.Println()

	// 往c中添加数据
	go func() {
		c <- 1
		c <- 2
	}()

	// 从c中可以获取数据
	e := <-c
	fmt.Println("v1:", e)

	// 从n.ch中也可以获取数据
	d := <-n.ch
	fmt.Println("v2:", d)

	fmt.Println()
	fmt.Println("&c:", &c)
	fmt.Println("&n:", &n.ch)
	fmt.Println("c:", c)
	fmt.Println("n:", n.ch)
}

type node struct {
	ch chan int
}
