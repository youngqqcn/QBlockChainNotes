package main

import (
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"github.com/hyperledger/fabric/protos/peer"
	"log"
)


type HelloWorld struct {


}

func (this *HelloWorld) Init( stub shim.ChaincodeStubInterface) peer.Response {


	args := stub.GetStringArgs()

	err := stub.PutState(args[0], []byte(args[1]))
	if err != nil {
		shim.Error(err.Error())
	}
	return  shim.Success(nil)
}




func (this *HelloWorld)Invoke(stub shim.ChaincodeStubInterface) peer.Response  {

	fn, args := stub.GetFunctionAndParameters()
	if fn == "set"{
		return this.set(stub, args)
	}else if fn == "get"{
		return this.get(stub, args)
	}
	return shim.Error("Invoke func error")
}

func (this *HelloWorld)set(stub shim.ChaincodeStubInterface,  args  []string)  peer.Response {
	err := stub.PutState(args[0], []byte(args[1]))
	if err != nil{
		return shim.Error(err.Error())
	}
	return shim.Success(nil)
}

func (this *HelloWorld)get(stub shim.ChaincodeStubInterface, args []string) peer.Response  {

	value, err := stub.GetState(args[0])
	if err != nil{
		return shim.Error(err.Error())
	}
	return shim.Success(value)
}



func main(){
	err := shim.Start(new(HelloWorld))
	if err != nil {
		log.Println(err)
		return
	}

}