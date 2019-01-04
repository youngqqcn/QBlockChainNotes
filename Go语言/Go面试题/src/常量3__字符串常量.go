
package main

import (
	"fmt"
)

const strConst = "hello"  //无类型常量
const typedhello string = "Hello World"   //有类型常量

func main() {
	fmt.Println("Hello, playground")
	var name = "Sam"  // 译者注：这里编译器需要推导出 name 的类型，
	// 那么它是如何从无类型的常量 "Sam" 中获取类型的呢？
	fmt.Printf("type %T value %v\n", name, name)
	fmt.Printf("type %T value %v\n", strConst, strConst)

}

/*
答案是无类型常量有一个默认的类型，当且仅当代码中需要无类型常量提供类型时，它才会提供该默认类型。
在语句 var name = "Sam" 中，name需要一个类型，因此它从常量 "Sam" 中获取其默认类型：string。
 */



