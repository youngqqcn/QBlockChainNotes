package main

import (
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"github.com/hyperledger/fabric/protos/peer"
	"fmt"
	"encoding/json"
	"bytes"
)

/**
*作者: yqq
*日期: 2018/12/27  11:39
*描述: 投票系统  chaincode
*/

type VoteChaincode struct {

}


type Vote struct {
	Username string `json:"username"`
	VoteNum int `json:"votenum"`
}



func (t *VoteChaincode)Init(stub shim.ChaincodeStubInterface) peer.Response  {

	return shim.Success(nil)
}

func (t *VoteChaincode)Invoke(stub shim.ChaincodeStubInterface) peer.Response  {

	fn, args := stub.GetFunctionAndParameters()
	if fn == "voteUser"{
		return t.voteUser(stub, args)
	}else if fn == "getUserVote"{
		return t.getUserVote(stub, args)
	}

	return shim.Error("方法不存在")
}

func (t *VoteChaincode)voteUser(stub shim.ChaincodeStubInterface, args []string ) peer.Response  {

	userName := args[0]


	userAsBytes , err := stub.GetState(userName)
	if err != nil{
		return shim.Error(err.Error())
	}

	vote := Vote{}
	if userAsBytes == nil{
		//如果用户不存在, 则创建用户
		vote = Vote{Username:userName, VoteNum:0}
	}else{
		err = json.Unmarshal(userAsBytes, &vote)
		if err != nil{
			return shim.Error(err.Error())
		}
		vote.VoteNum += 1
	}

	voteJsonAsBytes , err := json.Marshal(vote)
	if err != nil{
		return shim.Error(err.Error())
	}

	//存入数据库
	err = stub.PutState(userName, voteJsonAsBytes)
	if err != nil{
		return shim.Error(err.Error())
	}

	return shim.Success(nil)
}

func (t *VoteChaincode)getUserVote(stub shim.ChaincodeStubInterface, arg []string) peer.Response  {

	resultIterator , err := stub.GetStateByRange("", "")
	if err != nil{
		return shim.Error(err.Error())
	}
	defer resultIterator.Close()


	//组装json格式返回值
	isFirst := true
	var buffer bytes.Buffer
	buffer.WriteString("[")
	for resultIterator.HasNext(){
		queryResponse , err := resultIterator.Next()
		if err != nil{
			return shim.Error(err.Error())
		}

		if isFirst != true{
			buffer.WriteString(",")
			isFirst = false
		}

		buffer.WriteString(string(queryResponse.Value))
	}

	buffer.WriteString("]")
	fmt.Println(buffer.String())
	return shim.Success(buffer.Bytes())
}




func main() {
	err := shim.Start(new(VoteChaincode))
	if err == nil{
		fmt.Println(err.Error())
	}
}

