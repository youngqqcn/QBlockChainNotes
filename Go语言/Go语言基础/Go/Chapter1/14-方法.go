package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/28  9:52
*描述: 方法

	添加成员方法
	接收者:  值  或   指针
	注意:  在go语言中

	接收者               方法集
	T 				    func (t T)
	*T                  func (t T)  and  func (t *T)

*/


//1.基础类型作为接收者
type MyInt int
func (a MyInt/*接收者*/) MyAdd ( b MyInt) MyInt  {
	return  a + b
}

//2.结构体作为接收者
type Car struct {
	strName string
	nPrice int
	nSpeed int
}

func (car Car)showCarInfo()  {
	fmt.Println("================")
	fmt.Println(car.strName)
	fmt.Println(car.nPrice)
	fmt.Println(car.nSpeed)
	fmt.Println("================")
}

//3.指针作为接收者
func (pCar *Car)setPrice(nSetPrice int)  {
	pCar.nPrice = nSetPrice
}

//4.值作为接收者
func (pCar Car)setPriceByteValue(nSetPrice int)  {
	pCar.nPrice = nSetPrice
}



func main() {
	var  intA, intB MyInt = 10, 11
	fmt.Println(intA.MyAdd(intB))
	/////////////////////////////////

	car := Car{"法拉利", 2000000, 5000000}
	car.showCarInfo()
	////////////////////////////
	fmt.Println("")
	fmt.Println("")
	fmt.Println("")
	fmt.Println("")

	car.setPriceByteValue(9999999)
	fmt.Println("设置价格后(值传递)")
	car.showCarInfo()
	fmt.Println("")
	fmt.Println("")
	fmt.Println("")
	fmt.Println("")

	(&car).setPrice(55555555 )  ////go语言会自动解引用
	fmt.Println("设置价格后(值传递)")
	car.showCarInfo()


	car.setPrice(666666666)  //非接口类型调用 *T接收者方法时,
		                             // 编译器会做自动转换
		                             //注意: 当是接口时, 这样就不允许了!!!
	fmt.Println("设置价格后(值传递)")
	(&car).showCarInfo()  //会自动解引用  , 即和   car.ShowCarInfo() 等效


}
