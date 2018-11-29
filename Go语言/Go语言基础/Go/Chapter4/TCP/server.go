package main

import (
	"net"
	"log"
	"fmt"
	"strings"
)

/**
*作者: yqq
*日期: 2018/11/29  21:54
*描述:  服务端
*/

func dealConn(conn net.Conn)  {

	defer conn.Close()

	ipAddr := conn.RemoteAddr().String()
	fmt.Println(ipAddr, "连接成功")

	buf := make([]byte, 1024)  // []byte 和 string 可以相互转换

	for{
		len, err := conn.Read(buf) //阻塞读取
		if err != nil{
			fmt.Println(err)
			return
		}

		result := buf[:len]
		fmt.Printf("接收到数据来自[%s]===>[%d]:%s\n", ipAddr, len, string(result))

		if "exit" == string(result){
			fmt.Printf("%s退出", ipAddr)
			return
		}

		conn.Write([]byte(strings.ToUpper(string(result))))
	}
	
}



func main() {


	listenner, err  := net.Listen("tcp", "127.0.0.1:8000")
	if err != nil{
		log.Fatal(err)
	}
	defer listenner.Close()

	for {
		conn, err := listenner.Accept()
		if err != nil{
			log.Println(err)
			continue
		}
		go dealConn(conn)
	}

}

