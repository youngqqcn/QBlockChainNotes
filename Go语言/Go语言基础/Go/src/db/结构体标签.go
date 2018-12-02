package main

import (
	"reflect"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/12/2  20:33
*描述:

	go语言结构体  标签

*/


type USER struct{
	//Name string `标签:"标签内容"`
	Name string `标签`
}

func main() {

	user := USER{"yqq"}
	//fmt.Println(user.Name)

	t := reflect.TypeOf(user)
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		//fmt.Println(field.Tag.Get("标签"))
		fmt.Println(field.Tag)
		fmt.Printf("%T", field.Tag) //reflect.StructTag
	}
}


