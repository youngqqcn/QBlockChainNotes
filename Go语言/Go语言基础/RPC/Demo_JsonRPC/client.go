package main

import (
	"fmt"
	"log"
	"net/rpc/jsonrpc"
)


type ArgsTwo struct {
	A , B int
}


type QuotientTwo struct {
	Quo, Rem int
}


func main()  {

	//检查命令参数
	/*
	if len(os.Args) != 2{
		fmt.Println("Usage:" , os.Args[0], "server")
		os.Exit(1)
	}

	serverAddr := os.Args[1]
	*/
	serverAddr := "127.0.0.1"
	client, err := jsonrpc.Dial("tcp", serverAddr + ":11111")
	if err != nil{
		log.Fatal("dialing:", err)
	}

	args  := ArgsTwo{17, 9}
	var reply int
	err = client.Call("Math.Multiply", args, &reply)
	if err != nil{
		log.Fatal("Math Multiply error:", err)
	}

	fmt.Printf("Math: %d * %d = %d \n", args.A, args.B, reply)



	//除法
	var quo QuotientTwo
	err = client.Call("Math.Divide", args, &quo)
	if err != nil{
		log.Fatal("Math Devide error: ", err)
	}

	fmt.Printf("Math: %d / %d = %d   remainder=%d", args.A, args.B, quo.Quo, quo.Rem)


}