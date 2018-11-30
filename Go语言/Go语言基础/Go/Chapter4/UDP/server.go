package main

import (
	"net"
	"fmt"
	"strings"
)

/**
*作者: yqq
*日期: 2018/11/30  15:52
*描述: udp
*/

func main() {


	addr , err := net.ResolveUDPAddr("udp", "127.0.0.1:9999")
	if err != nil{
		fmt.Println(err)
		return
	}

	conn, err := net.ListenUDP("udp", addr)
	if err != nil{
		fmt.Println(err)
		return
	}
	defer conn.Close()

	for{
		buf := make([]byte, 1024)
		len, cliAddr, err := conn.ReadFromUDP(buf)
		if err != nil{
			fmt.Println("conn.ReadFromUDP() error")
			return
		}

		if len == 0{
			return
		}

		strSend := strings.ToUpper(string(buf[:len]))
		len , err = conn.WriteToUDP([]byte(strSend), cliAddr)
		if err != nil{
			fmt.Println("WriteToUDP() err")
			return
		}
		//发送成功
		fmt.Println("send:", strSend)
	}

}
