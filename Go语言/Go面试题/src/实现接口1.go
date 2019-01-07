package main

import (
	"fmt"
	"lib"
	"errors"
)

/**
*作者: yqq
*日期: 2019/1/7  23:06
*描述: 实现接口
*/

//const (
//	ERR_ELEM_EXIST error = errors.New("element already exists")
//	ERR_ELEM_NT_EXIST error = errors.New("element not exists")
//)

type Fighter struct {
}

func (this *Fighter)Say()  {

	fmt.Println("hello")

}


type Children struct {

}

func (this *Children)Say()  {
	fmt.Println("Children")

}




func main() {

	var  humaner  lib.Humaner
	humaner = new(Fighter)
	humaner.Say()


	str := "abc" + "123"

	children := Children{}
	humaner = &children

	humaner.Say()

}
