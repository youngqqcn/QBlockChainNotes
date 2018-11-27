package main

import (
	"os"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/11/21  19:23
*描述: 延迟调用


*/

func main() {

	fout , err := os.Create("test.txt")
	if  err != nil{
		fmt.Println(err)
		return
	}
	defer fout.Close() //延迟关闭文件

	for i := 0; i < 100; i++{
		outputStr := fmt.Sprintf("%s:%d", "Line", i)
		fout.WriteString(outputStr)
		fout.Write(	[]byte("hello golang\n"))
	}
	fmt.Println("写入文件完成")

}
