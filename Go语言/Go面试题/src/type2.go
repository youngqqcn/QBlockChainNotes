
package main
import "fmt"


/*
编译执行下面代码会出现什么?
 */



func main()  {
	type MyInt1 int
	type MyInt2 = int
	var i int =9
	var i1 MyInt1 = i
	var i2 MyInt2 = i
	fmt.Println(i1,i2)

	//fmt.Printf("%T ", i2)
}


























































/*


//Go 1.9 新特性 Type Alias
func main()  {
	type MyInt1 int               //创建了新类型definition
	type MyInt2 = int            //给一个类型区别名  alias
	var i int =9
	var i1 MyInt1 = i
	var i2 MyInt2 = i
	fmt.Println(i1,i2)
}
 */