package main

import (
	"net/http"
	"log"
	"fmt"
	"strings"
	"html/template"
)

/**
*作者: yqq
*日期: 2018/12/1  15:00
*描述: 处理表达的输入


*/



func sayHelloName2(w http.ResponseWriter, r *http.Request){

	r.ParseForm()


	fmt.Println("method:", r.Method)
	fmt.Println(r.Form)
	fmt.Println("path:", r.URL.Path)
	fmt.Println("scheme:", r.URL.Scheme)
	fmt.Println(r.Form["url_long"])

	for k, v := range  r.Form{
		fmt.Println("key:", k)
		fmt.Println("value:", strings.Join(v, ""))
	}

	fmt.Fprintf(w, "这是一个简单的web服务器")

}



func login(w http.ResponseWriter, r *http.Request){

	r.ParseForm()  // 解析表单, 之后才能对表单数据进行操作

	fmt.Println("method:", r.Method)

	if r.Method == "GET"{
		t, err := template.ParseFiles("./Chapter5/login.html")
		if err != nil{
			log.Println(err)
			return
		}
		log.Println(t.Execute(w, nil))
	}else{  //POST请求
		fmt.Println("username:", r.Form["username"])
		fmt.Println("password:", r.FormValue("password"))
		fmt.Println("fruit:", r.Form.Get("fruit"))
	}

}


func fruit(w http.ResponseWriter, r *http.Request){

	r.ParseForm()  // 解析表单, 之后才能对表单数据进行操作

	fmt.Println("method:", r.Method)


	if r.Method == "GET"{
		t, err := template.ParseFiles("./Chapter5/下拉菜单.html")
		if err != nil{
			log.Println(err)
			return
		}
		log.Println(t.Execute(w, nil))
	}else{  //POST请求

		fmt.Println("请求的url是:", r.URL.RawQuery)


		//验证表单输入的数据
		bOk := func() bool{
			fruits := []string{"apple", "pear", "banana", "watermelon"}
			for _, v := range fruits {
				if v == r.Form.Get("fruit") {
					return true
				}
			}
			return false
		}()

		if !bOk {
			fmt.Fprintf(w, "你选择的水果不合法, 请重新选择")
			return
		}



		fmt.Println("选择的水果是:", r.Form.Get("fruit"))
	}

}

func singleBtn(w http.ResponseWriter, r *http.Request)  {


	if  r.Method == "GET"{
		t, err := template.ParseFiles("./Chapter5/单选按钮.html")
		if err != nil{
			log.Println(err)
			return
		}
		log.Println(t.Execute(w, nil))
		return
	}

	r.ParseForm() //解析表单数据

	gender := r.Form.Get("gender")
	bOk := func () bool{
		for _, v := range []string{"1", "2"} {
			if v == gender {
				return true
			}
		}
		return false
	}()

	if !bOk{
		fmt.Fprintf(w, "你的选择不合法")
		return
	}

	fmt.Println(r.Form.Get("gender"))

}

func mulSelBox(w http.ResponseWriter, r *http.Request)  {

	if r.Method == "GET"{
		//返回网页
		t, err := template.ParseFiles("./Chapter5/复选框.html")
		if err != nil{
			log.Println(err)
			return
		}

		log.Println(t.Execute(w, nil))
		return
	}

	//POST
	r.ParseForm()

	//interests := r.FormValue("interest")  //FormValue返回key为键查询r.Form字段得到结果[]string切片的第一个值
	fmt.Println(r.Form["interest"])
	
}



func main() {

	http.HandleFunc("/", sayHelloName2)
	http.HandleFunc("/login", login)
	http.HandleFunc("/fruit", fruit)
	http.HandleFunc("/gender", singleBtn)
	http.HandleFunc("/mulSelBox", mulSelBox)


	err := http.ListenAndServe(":9999", nil)
	if err != nil{
		log.Fatal("listenAndServe: ", err)
	}

}
