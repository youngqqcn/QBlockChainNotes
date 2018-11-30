package main

import (
	"net"
	"log"
	"bufio"
	"os"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/11/30  15:53
*描述:  udp client
*/

func main() {


	conn, err := net.Dial("udp", "127.0.0.1:9999")
	if err != nil{
		log.Fatal(err)
		return
	}
	defer conn.Close()

	buf := make([]byte, 1024)
	input := bufio.NewScanner(os.Stdin)
	for input.Scan(){
		strInput  := input.Text()
		len,err := conn.Write([]byte(strInput))
		if err != nil{
			fmt.Println(err)
			return
		}
		fmt.Println("发送了" , len, " 个字节")

		//阻塞接收服务器返回数据
		 len, err = conn.Read(buf)
		 if err != nil{
		 	fmt.Println(err)
			 return
		 }
		 fmt.Println("接收到:", string(buf[:len]))
	}
}
