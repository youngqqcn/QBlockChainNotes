package main

import "fmt"

// var a string
// var done bool

// func setup() {
// 	a = "hello, world\n"
// 	done = true
// }

// func main() {
// 	go setup()
// 	for !done {
// 	}
// 	print(a)
// }

// func main() {
//     go println("你好, 世界")
// }

// package main

// import "fmt"

func main() {
	var ch chan int
	go func() {
		fmt.Println("B")
		ch <- 0
	}()
	<-ch
	fmt.Println("A")
}

// func main() {
// 	var ch chan int
// 	fmt.Println(ch)  // nil
// 	ch2 := make(chan int)
// 	fmt.Println(ch2) // 0xc000192000
// }
