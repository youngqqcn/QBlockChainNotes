package main

import (
	"net"
	"log"
	"os"
	"fmt"
	"io"
		)

/**
*作者: yqq
*日期: 2018/11/30  9:31
*描述: 文件发送方
*/

func main() {

	//创建socket
	conn, err := net.Dial("tcp", "127.0.0.1:8888")
	if err != nil{
		log.Fatal(err)
		return
	}
	defer conn.Close() //记得关闭


	//文件操作
	fmt.Println("请输入文件路径:")
	var  inputStr string
	fmt.Scan(&inputStr)
	fmt.Println("输入的文件路径:", inputStr)

	strPath := inputStr
	//strPath := `G:\视频\go开发实战\第07天(网络概述、socket编程)\3-视频\31_并发聊天服务器：超时处理.avi`
	reader, err := os.Open(strPath)
	if  err != nil{
		fmt.Println(err.Error())
		return
	}
	defer reader.Close()

	//1.先发送文件名

	//splits := strings.Split(strPath, "\\")
	//strFileName := splits[len(splits) - 1]

	fileInfo , err  := os.Stat(strPath)
	if err != nil{
		fmt.Println(err.Error())
		return
	}
	strFileName := fileInfo.Name()  //获取到文件名
	conn.Write([]byte(strFileName)) //发送文件名


	//等待接收方返回,接收文件名是否成功的信息
	buf := make([]byte, 1024 * 4)
	len, err := conn.Read(buf)
	if err != nil{
		fmt.Println(err)
		return
	}
	if string(buf[:len]) == "200"{
		fmt.Println("文件名发送成功")
	}else{
		fmt.Println("文件名发送失败")
		return
	}

	//2.发送文件内容
	for{
		len , err := reader.Read(buf)
		if err != nil{
			if err == io.EOF{
				fmt.Println("文件已发送完毕")
			}else{
				fmt.Println(err)
			}
			return
		}
		conn.Write(buf[:len]) //读出来多少, 发送多少
	}
}
