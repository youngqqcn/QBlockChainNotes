package main

import (
	"strings"
	"fmt"
	"strconv"
)

/**
*作者: yqq
*日期: 2018/11/28  16:47
*描述:
		字符串处理
*/

func main() {

	strTest := "hellowoerkdfldfok"


	//strings.Split
	for i, v := range  strings.Split(strTest,  "o" ){
		fmt.Printf("%d --> %s\n", i, v)
	}

	//strings.Contains
	fmt.Println("=========================")
	if ok :=  strings.Contains(strTest, "hell"); ok{
		fmt.Println("yes")
	}

	//utf-8编码
	//strings.ContainsRune(strTest, 999/*这是utf-8编码*/ )


	//字符串转为 数值型
	intTmp , err2 := strconv.Atoi("9999")
	floatTmp, err1 := strconv.ParseFloat("999.99", 8)
	if  err1 != nil {
		fmt.Println(err1.Error())
	}else if err2 != nil{
		fmt.Println(err2.Error())
	}else{
		fmt.Printf("%T    %d\n", intTmp, intTmp)
		fmt.Printf("%T    %f\n", floatTmp, floatTmp)
	}




}
