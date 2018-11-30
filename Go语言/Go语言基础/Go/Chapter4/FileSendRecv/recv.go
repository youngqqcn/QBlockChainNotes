package main

import (
	"net"
	"log"
	"fmt"
	"os"
	"io"
)

/**
*作者: yqq
*日期: 2018/11/30  9:31
*描述:  文件接收方
*/

func recvFile(conn net.Conn)  {
	//1.先接收文件名
	nameBuf := make([]byte, 1024)
	len, err := conn.Read(nameBuf)
	if err  != nil{
		fmt.Println(err)
		return
	}
	if len == 0{
		fmt.Println("文件名为空, 请确认")
		conn.Write([]byte("500")) //返回一个 200 表示文件名接收成功
		return
	}
	conn.Write([]byte("200")) //返回一个 200 表示文件名接收成功

	//创建文件
	strFileName := string(nameBuf[:len])
	fOut, err := os.Create(string(strFileName))
	if err != nil{
		fmt.Println(err)
		return
	}
	defer fOut.Close()
	fmt.Println("开始接收文件", strFileName)

	buf := make([]byte, 1024 * 4)
	for {
		len, err := conn.Read(buf)
		if err != nil {
			if err == io.EOF{
				fmt.Println("文件接收完毕")
			}else {
				fmt.Println(err)
			}
			return
		}
		if len == 0{
			fmt.Println("文件接收完毕")
			return
		}
		fOut.Write(buf[:len]) //接收了多少, 写多少
	}
}



func main() {

	//监听端口
	listener , err := net.Listen("tcp", "127.0.0.1:8888")
	if err != nil{
		log.Fatal(err)
		return
	}
	defer listener.Close()

	//阻塞等待连接
	//for{
		conn, err := listener.Accept()

		if err != nil{
			fmt.Println(err.Error())
			return
		}

		recvFile(conn)
	//}
}

