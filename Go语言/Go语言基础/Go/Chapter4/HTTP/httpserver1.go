package main

import (
	"net/http"
	"log"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/11/30  15:30
*描述: http服务器
*/

func handler(w http.ResponseWriter, req *http.Request)  {

	fmt.Println("请求方法: ", req.Method)
	fmt.Println("头部: ", req.Header)

	w.Write([]byte("你好,这是一个测试http服务器."))
}

func main() {
	http.HandleFunc("/", handler)
	log.Printf("listen on 9999\n")

	err := http.ListenAndServe(":9999", nil)
	if err != nil{
		log.Fatal(err)
	}

}
