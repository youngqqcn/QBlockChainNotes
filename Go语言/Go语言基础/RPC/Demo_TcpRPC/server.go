package main

import (
	"fmt"
	"errors"
	"net"
	"os"
	"net/rpc"
)

type Args struct {
	A , B int
}

type Math int 
//func () NAME  (ARGS TYPE, REPLY *TYPE) error

func (m *Math) Multiply(args *Args, reply *int) error {

	*reply  = args.A * args.B
	return nil
}

type Quotient struct {
	Quo, Rem int
} 

func (m *Math)Divide(args *Args, quo *Quotient) error {

	if(args.B == 0){
		return errors.New("divide by zero")
	}

	quo.Quo = args.A / args.B  //商
	quo.Rem = args.A % args.B  //余数

	return  nil
}

func main()  {

	math := new(Math)

	rpc.Register(math)

	tcpAddr , err := net.ResolveTCPAddr("tcp", ":9999")
	if err != nil{
		fmt.Println("Fatal error", err)
		os.Exit(2)
	}

	listener, err := net.ListenTCP("tcp", tcpAddr )
	if err != nil{
		fmt.Println("Fatal error", err)
		os.Exit(2)
	}


	for{
		conn, err := listener.Accept()
		if err != nil{
			fmt.Println("Fatal error", err)
			os.Exit(2)
		}

		rpc.ServeConn(conn)
	}

}







