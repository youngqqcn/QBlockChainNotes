package main

import (
	"net/rpc"
	"net/http"
	"fmt"
	"errors"
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
	rpc.HandleHTTP()

	err := http.ListenAndServe(":9999", nil)
	if err == nil{
		fmt.Println(err.Error())
	}

	fmt.Printf("startup success....")

}







