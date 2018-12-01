package main

import (
	"net/http"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/12/1  11:31
*描述:

要实现处理函数
		handler func(ResponseWriter, *Request))



*/



func _sayHelloName(w http.ResponseWriter,  r *http.Request)  {
	fmt.Fprintf(w, "你好, 这是一个简单web服务器")
}



func main() {

	http.HandleFunc("/",  _sayHelloName)

	err := http.ListenAndServe("127.0.0.1:9999", nil)
	if err != nil{
		fmt.Println(err)
	}

}
