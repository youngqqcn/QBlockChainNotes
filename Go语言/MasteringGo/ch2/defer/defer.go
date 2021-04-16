package main

import "fmt"


func d1()  {
	for i := 3; i > 0; i-- {
		defer fmt.Printf("%d ", i)
	}
	fmt.Println()
}

func d2() {
	for i := 3; i > 0; i-- {
		defer func() {
			fmt.Printf("%d ", i) // NOTE: wrong 
		}()
	}
	fmt.Println()
}

func d3() {
	for i := 3; i > 0; i-- {
		defer func(i int) {
			fmt.Printf("%d ", i)
		}(i)
	}
	fmt.Println()
}

func main() {
	d1()
	fmt.Println("============")
	d2();
	fmt.Println("============")
	d3();
	fmt.Println("============")
}