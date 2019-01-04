package main

import "fmt"

func GetValue(m map[int]string, id int) (string, bool) {
	if _, exist := m[id]; exist {
		return "存在数据", true
	}
	return nil, false
}
func main()  {
	intmap:=map[int]string{
		1:"a",
		2:"bb",
		3:"ccc",
	}


	v,err:=GetValue(intmap,3)
	fmt.Println(v,err)
}




















































/*
nil 可以用作 interface、function、pointer、map、slice 和 channel 的“空值”。
但是如果不特别指定的话，Go 语言不能识别类型，
所以会报错。报:cannot use nil as type string in return argument.
 */