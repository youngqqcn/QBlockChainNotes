

package main

import "fmt"

func func1()  {

	var defaultName = "Sam" //allowed
	var customName string = "Jack" //allowed
	customName = defaultName //allowed   内置类型可以


	fmt.Println(customName )
	fmt.Println(defaultName)
}


func func2(){

	var defaultName = "Sam" //allowed

	type MyString string
	var customName  MyString = "Jack" //allowed
	//customName = defaultName // error   不能混用


	fmt.Println(customName )
	fmt.Println(defaultName)

}

func main() {

	func1()
	func2()

}
