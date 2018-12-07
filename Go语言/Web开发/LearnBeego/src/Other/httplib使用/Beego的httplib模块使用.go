package main

import (
	"github.com/astaxie/beego/httplib"
		"fmt"
)

/**
*作者: yqq
*日期: 2018/12/7  10:02
*描述: 使用httplib模块
*/

func main() {

	req := httplib.Get("http://beego.me")
	//str, err := req.String()
	//if err != nil{
	//	log.Fatal(err)
	//}
	//fmt.Println(str)
	//fmt.Println("===========================")


	res , err := req.Response()


	var buf[]byte
	len, err := res.Body.Read(buf)
	if err != nil{
		fmt.Println("Read err:", err)
		return
	}
	fmt.Println(len)
	fmt.Println(string(buf))



}
