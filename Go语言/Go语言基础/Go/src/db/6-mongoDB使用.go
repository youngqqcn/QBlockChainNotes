package main

import (
	"gopkg.in/mgo.v2"
	"fmt"
	"log"
	"gopkg.in/mgo.v2/bson"
)

/**
*作者: yqq
*日期: 2018/12/3  10:52
*描述:
	mongoDB 使用
*/

type  Person struct{
	Name string
	Phone string
}



func main() {

	//session , err := mgo.Dial("127.0.0.1")
	session , err := mgo.Dial("192.168.150.138") //Ubuntu
	if err  != nil{
		panic(err)
	}
	defer session.Close()
	fmt.Println("启动连接成功")


	session.SetMode(mgo.Monotonic, true)

	c := session.DB("test").C("people")
	err = c.Insert(&Person{"yqq", "44232343423"},
				&Person{"Jack", "3429982522"})
	if err != nil{
		log.Fatal(err)
	}

	result := Person{}
	err = c.Find(bson.M{"name":"Jack"}).One(&result)
	if err != nil{
		log.Fatal(err)
	}

	fmt.Println("Phone", result.Phone)

}
