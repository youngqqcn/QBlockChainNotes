

package main

import (
	"fmt"
	"math"
)

func main() {
	fmt.Println("Hello, playground")
	var a = math.Sqrt(4)//allowed
	const b = math.Sqrt(4)//not allowed
	//const c = 0
}





























































/*
常量的值必须在编译期间确定。因此不能将函数的返回值赋给常量，因为函数调用发生在运行期。
 */