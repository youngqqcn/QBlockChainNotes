package main

import (
	"fmt"
	"reflect"
)


func main1()  {
	defer func() {
		if err:=recover();err!=nil{
			fmt.Println(err)
		}else {
			fmt.Println("fatal")
		}
	}()

	defer func() {
		panic("defer panic")
	}()
	panic("panic")
}

func main()  {
	defer func() {
		if err:=recover();err!=nil{
			fmt.Println("++++")
			f:=err.(func()string)
			fmt.Println(err,f(),reflect.TypeOf(err).Kind().String())
		}else {
			fmt.Println("fatal")
		}
	}()

	defer func() {
		panic(func() string {
			return  "defer panic"
		})
	}()
	panic("panic")
}













































//panic仅有最后一个可以被revover捕获
