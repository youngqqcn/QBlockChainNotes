package main

import (
	"github.com/astaxie/beego/config"
		"log"
	"fmt"
	"os"
)

/**
*作者: yqq
*日期: 2018/12/7  10:41
*描述:  config 模块使用
*/

func main() {


	os.Create("test.txt")

	//inicfg, err := config.NewConfig("ini", `C:\Users\yqq\Desktop\QBlockChainNotes\Go语言\Web开发\LearnBeego\src\Other\config模块使用\test.conf`)
	inicfg, err := config.NewConfig("ini", "./src/Other/config模块使用/test.conf")
	if err != nil{
		log.Fatal(err)
	}

	name := inicfg.String("name")
	fmt.Println(name)


	// section
	fmt.Println( inicfg.Int64("info::age"))
	fmt.Println( inicfg.String("info::email"))
	fmt.Println( inicfg.String("info::addr"))

}

