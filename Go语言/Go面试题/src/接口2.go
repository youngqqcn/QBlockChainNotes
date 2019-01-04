
package main

import (
"fmt"
)


//以下代码打印出来什么内容，说出为什么



type People2 interface {
	Show()
}
type Student struct{}

func (stu *Student) Show() {

}

func live() People2 {
	var stu *Student
	return stu
}

func main() {
	stu := live()
	if stu == nil {
		fmt.Println("AAAAAAA")
	} else {
		fmt.Println("BBBBBBB")
	}
}
