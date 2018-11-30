package main

import (
	"net"
	"fmt"
	"time"
)

/**
*作者: yqq
*日期: 2018/11/30  11:06
*描述: 并发聊天服务器

客户端使用  nc.exe

*/


type Cli struct {
	ipAddr string
	name string
	C    chan string
}

var gCliMap = make(map[string]Cli)
var gChMessage = make(chan string)


func handleConn(conn net.Conn)  {
	defer conn.Close()


	gChMessage <- conn.RemoteAddr().String() + string("login....\n")

	cli := Cli{ipAddr:conn.RemoteAddr().String(), name:conn.RemoteAddr().String(), C : make(chan string)}

	//加入到 gCliMap
	gCliMap[conn.RemoteAddr().String()] = cli

	var gChQuit = make(chan  bool)

	//向当前客户端发送消息
	go func() {
		for msg := range cli.C{
			conn.Write([]byte(msg))
		}
	}()

	//接收当前客户端发送来消息
	go func() {
		recvBuf := make([]byte, 1024)

		for{
			len ,err := conn.Read(recvBuf)
			if len == 0{
				gChQuit <- true
				return
			}
			if err != nil{
				fmt.Println(err)
				return
			}
			gChMessage <- conn.RemoteAddr().String() + ": " + string(recvBuf[:len])
		}

	}()


	//for {
		select {
		case <- gChQuit:
			delete(gCliMap, conn.RemoteAddr().String())
			gChMessage <- conn.RemoteAddr().String() + " exit...\n"

			//打印, 还剩几个用户
			strTmp := fmt.Sprintf( "left %d client\n", len(gCliMap) )
			gChMessage <- strTmp
			return

		case <- time.After(10 * time.Second):  //超时
			delete(gCliMap, conn.RemoteAddr().String())
			gChMessage <- conn.RemoteAddr().String() + " timeout ...\n"

			//打印, 还剩几个用户
			strTmp := fmt.Sprintf( "left %d client\n", len(gCliMap) )
			gChMessage <- strTmp
			return

		//default:

		}
	//}


}

func main()  {

	listener , err := net.Listen("tcp", "127.0.0.1:8888")
	if err != nil{
		fmt.Println(err)
		return
	}
	defer listener.Close()


	//从 gChMessage中获取消息, 向所有客户端广播
	go func() {
		for {
			msg := <- gChMessage
			for _, cli := range gCliMap {
				cli.C <-  msg
			}
		}
	}()


	for {
		conn, err := listener.Accept()
		if err != nil{
			fmt.Println(err)
			return
		}

		go handleConn(conn)
	}

	
}
