package main

import "C"
import "fmt"


//export Mul
func Mul(a, b int) int  {
	return a * b
}

//export PrintMessage
func PrintMessage(){
	fmt.Println("goooooooooooood")
}

func main() {

}
