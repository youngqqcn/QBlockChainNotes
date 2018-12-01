package main

import (
	"net/http"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/12/1  11:17
*描述: 自己实现简单路由设置


//Handler是一个接口,  只要实现  ServeHTTP 这个方法, 就可以实现自定义路由

type Handler interface {
	ServeHTTP(ResponseWriter, *Request)  // 路由实现
}


要理解 Go 的web运行过程, 可以断点调试

*/


type MyMux struct {

}

func (pMyMux *MyMux)ServeHTTP( w http.ResponseWriter, r *http.Request )  {

	if r.URL.Path == "/" {
		sayHelloName(w, r)
		return
	}
	http.NotFound(w, r)
	return
}

func sayHelloName(w http.ResponseWriter, r *http.Request)  {
	fmt.Fprintf(w, "你好, 这是我自己写的路由")
}


func main() {

	mux := &MyMux{}
	http.ListenAndServe(":9999", mux)
}
