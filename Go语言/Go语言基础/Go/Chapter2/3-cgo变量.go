package main

import "C"
import "fmt"


func main(){

	var n C.int
	n = 5
	fmt.Println(n)


	var m1 int
	m1 = int(n + 3)
	fmt.Println(m1)

}
