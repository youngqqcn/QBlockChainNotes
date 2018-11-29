package main

import (
	"fmt"
	"reflect"
)

/**
*作者: yqq
*日期: 2018/11/29  9:00
*描述:
		反射机制


	反射类型:
		reflect.Type   reflect.Value


*/


func main() {

	var x float64 = 3.4

	//1.类型获取与转换
	//interface{} ---> 反射类型
	fmt.Printf("Type:%v\n", reflect.TypeOf(x))
	fmt.Printf("Type:%v\n", reflect.ValueOf(x))
	fmt.Printf("Type:%T\n", reflect.ValueOf(x)) //reflect.Value


	//反射类型  ---> interface{}
	y := reflect.ValueOf(x).Interface().(float64)
	fmt.Printf("Type:%T\n", reflect.ValueOf(x).Interface())
	fmt.Printf("Type:%v\n", y) //reflect.Value
	fmt.Printf("Type:%T\n", y) //reflect.Value


	//2.修改值
	fmt.Println("===============================")
	//fmt.Printf("Type:%T\n", reflect.ValueOf(&x)) //reflect.Value
	z := reflect.ValueOf(&x).Elem()    //一定要是 指针
										//reflect.Value.Elem() 表示获取原始值对应的反射对象，
										// 只有原始对象才能修改，当前反射对象是不能修改的

	if z.CanSet(){     //newValue.CantSet()表示是否可以重新设置其值，
	                   // 如果输出的是true则可修改，否则不能修改
		z.SetFloat(999.9)
		fmt.Println("z=", z)
		fmt.Println("x=", x)
	}else{
		fmt.Println("不能设置值" )
	}


	//3.方法调用(核心用法)
	fmt.Println("===============================")
	user := User{"yqq", 5, 23,}

	reflectValue := reflect.ValueOf(user)
	methodValue := reflectValue.MethodByName("ShowUserInfoArgs")
	//if methodValue.Interface() == nil{
	//	fmt.Println("未找到方法")
	//	return
	//}

	args := []reflect.Value{reflect.ValueOf("yqq"), reflect.ValueOf(24)} //函数参数
	methodValue.Call(args)

	//无参数的
	methodValue2 := reflectValue.MethodByName("ShowUserInfo")
	methodValue2.Call(make([]reflect.Value, 0))



	//4.显示一个类型的方法集
	fmt.Println("===========================")
	for i := 0; i < reflect.ValueOf(user).NumMethod(); i++{
		fmt.Println(reflect.ValueOf(user).Type().Method(i).Name)
	}


	//5.对于未知类型
	fmt.Println("===============================")
	GetFiledAndMethod(user)



}


func GetFiledAndMethod(input interface{}){

	getType := reflect.TypeOf(input)
	getValue := reflect.ValueOf(input)
	fmt.Println(getType.Name())
	fmt.Println(getValue)

	//获取所有字段
	for i := 0; i < getType.NumField(); i++{

		field := getType.Field(i)
		fieldValue := getValue.Field(i)
		fmt.Printf("%T\n", fieldValue)
		fmt.Printf("%s: %v     \n",  field.Name, field.Type) //ok
		fmt.Printf("%s: %v   %v \n",  field.Name, field.Type,  fieldValue)
		//fmt.Printf("%s: %v   =  %v\n",  field.Name, field.Type, fieldValue)
	}

}


type User struct {
	strName string
	nId		int
	nAge	int
}

func (user User)ShowUserInfoArgs(name string, nAge int )  {
	fmt.Println("ShowUserInfoArgs", "name:", name, " age:", nAge, "raw name:", user.strName )
}

func (user User)ShowUserInfo()  {
	fmt.Println("ShowUserInfo", "name:", user.strName, " age:", user.nAge, "name:", user.strName )
}


