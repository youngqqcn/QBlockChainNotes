package main

import (
	"encoding/json"
	"fmt"
	"os"
)

/**
*作者: yqq
*日期: 2018/12/3  14:33
*描述: json文件操作

	1.解析JSON
	2.解析未知结构的json(interface+type assert  或 https://github.com/bitly/go-simplejson)
	2.输出JSON文件



注意:
Marshal函数只有在转换成功的时候才会返回数据，在转换的过程中我们需要注意几点：
	1.JSON对象只支持string作为key，所以要编码一个map，
        那么必须是map[string]T这种类型(T是Go语言中任意的类型)
	2.Channel, complex和function是不能被编码成JSON的
	3.嵌套的数据是不能编码的，不然会让JSON编码进入死循环
	4.指针在编码的时候会输出指针指向的内容，而空指针会输出null

*/


//4.使用 struct tag 控制json解析
type Server struct {
	ID int `json:"-"`   // "-" 表示不导出到json

	ServerName string `json:"serverName"`
	ServerName2 string  `json:"serverName2,string"`

	ServerIP string   `json:"serverIP,omitempty"`

}

func main()  {
	s := Server {
		ID : 3,
		ServerName: `Go "1.11"`,
		ServerName2: `Go "1.11"`,
		ServerIP: ``,
	}

	data, err := json.Marshal(s)
	if err != nil{
		fmt.Println(err)
		return
	}

	//os.Stdout.Write(data)
	fmt.Println(string(data))

	outFile, err :=	os.Create("./Chapter7/output.json")
	if err != nil{
		fmt.Println(err)
		return
	}
	defer outFile.Close()
	outFile.Write(data)



}


/*

//3.生成JSON
type Server struct {
	ServerName string
	ServerIP string
}


type ServerSlice struct {
	Servers []Server
}

func main()  {
	var s ServerSlice
	s.Servers = append(s.Servers, Server{ServerName:"Shanghai_VPN", ServerIP:"127.0.0.1"})
	s.Servers = append(s.Servers, Server{ServerName:"Shenzhen_VPN", ServerIP:"192.0.0.1"})

	data, err := json.Marshal(s)
	if err != nil{
		fmt.Println(err)
		return
	}


	fmt.Println(string(data))

}
*/







/*
//2.解析未知结构的json  使用  github.com/bitly/go-simplejson"
import (
	"github.com/bitly/go-simplejson"
	"fmt"
)

func main()  {

	js, err :=   simplejson.NewJson([]byte(`{
	"test": {
		"array": [1, "2", 3],
		"int": 10,
		"float": 5.150,
		"bignum": 9223372036854775807,
		"string": "simplejson",
		"bool": true
	}
	}`))

	if err != nil{
		fmt.Println(err)
		return
	}

	arr, _ := js.Get("test").Get("array").Array()
	i, _ := js.Get("test").Get("int").Int()
	ms := js.Get("test").Get("string").MustString()
	bignum , _:= js.Get("test").Get("bignum").Int64()

	fmt.Println(arr)
	fmt.Println(i)
	fmt.Println(ms)
	fmt.Println(bignum)

}

*/




/*
//1.解析JSON
type Server struct {
	ServerName string
	ServerIP string
}


type ServerSlice struct {
	Servers []Server
}




func main() {
	var s ServerSlice


	jsonFile, err := os.Open("./Chapter7/test.json")
	if err != nil{
		fmt.Println(err)
		return
	}
	defer jsonFile.Close()

	data , err:= ioutil.ReadAll(jsonFile)
	if err != nil{
		fmt.Println(err)
		return
	}
	json.Unmarshal(data, &s)

	fmt.Println(s)


}
*/
