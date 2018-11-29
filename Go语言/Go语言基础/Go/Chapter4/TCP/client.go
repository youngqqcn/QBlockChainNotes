package main

import (
	"net"
	"log"
	"fmt"
	"bufio"
	"os"
)

/**
*作者: yqq
*日期: 2018/11/29  22:07
*描述: 客户端
*/

func main() {

	conn, err := net.Dial("tcp", "127.0.0.1:8000")
	if err != nil{
		/*
		log.Fatal 函数执行过程,  和panic不同的是, log.Fatal 不会调用defer
		1.打印输出内容
		2.退出应用程序
		3.defer函数不会执行
		 */
		log.Fatal(err)
	}
	defer  conn.Close()

	buf := make([]byte, 1024)

	for{
		fmt.Printf("请输入发送内容:")

		//fmt.Scanf("%s", &buf)   //scanf  scan  都是 以空白符(空格)分隔,
									// 	遇到换行符停止, 而遇到  "hello world" 则会被分成两段

		input  := bufio.NewReader(os.Stdin) //从控制台读取, 可以读取包含空格的,  例如  "hello world"
		strInput, err := input.ReadString('\n')
		if err != nil{
			fmt.Println(err)
			return
		}

		fmt.Printf("发送的内容:%s\n", string(strInput))
		conn.Write([]byte(strInput))
		len, err := conn.Read(buf) //阻塞等待 服务器回复
		if err != nil{
			fmt.Println(err)
			return
		}

		result := buf[:len]
		fmt.Printf("接收到数据[%d]:%s\n", len, string(result))
	}
}
