package main

import (
	"github.com/julienschmidt/httprouter"
	"net/http"
	"fmt"
	"log"
)

/**
*作者: yqq
*日期: 2018/12/4  0:03
*描述: go实现 RESTful设计
*/

func Index(w http.ResponseWriter, r *http.Request, p httprouter.Params)  {

	fmt.Fprintf(w, "欢迎! 这是主页!\n")

}

func Hello(w http.ResponseWriter, r *http.Request, params httprouter.Params)  {
	fmt.Fprintf(w, "Hello, %s!\n", params.ByName("name") )

}

func getuser(w http.ResponseWriter, r *http.Request, params httprouter.Params)  {
	uid := params.ByName("uid")
	fmt.Fprintf(w, "you are get user %s", uid)
}


func modifyuser(w http.ResponseWriter, r *http.Request, params httprouter.Params)  {
	uid := params.ByName("uid")
	fmt.Fprintf(w, "you are modify user %s", uid)
}


func deleteuser(w http.ResponseWriter, r *http.Request, params httprouter.Params)  {
	uid := params.ByName("uid")
	fmt.Fprintf(w, "you are delete user %s", uid)
}


func adduser(w http.ResponseWriter, r *http.Request, params httprouter.Params)  {
	uid := params.ByName("uid")
	fmt.Fprintf(w, "you are add user %s", uid)
}




func main() {

	router := httprouter.New()
	router.GET("/", Index) //默认页面

	//如果访问 http://127.0.0.1:9999/hello/yqq 则返回  hello , yqq!
	router.GET("/hello/:name", Hello)

	router.GET("/user/:uid", getuser)

	//绝大多数web服务器，都不允许静态文件响应POST,PUT,DELETE请求，否则会返回“HTTP/1.1 405 Method not allowed”错误。
	//可以修改成表单形式,提交
	//router.POST("/adduser/:uid", adduser)
	//router.PUT("/modifyuser/:uid", modifyuser)
	//router.DELETE("/deleteuser/:uid", deleteuser)


	if err := http.ListenAndServe(":9999", router) ; err != nil{
		log.Fatal(err)
	}



}