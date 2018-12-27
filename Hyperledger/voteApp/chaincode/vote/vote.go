package main

import(
	"fmt"
	"encoding/json"
	"bytes"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"github.com/hyperledger/fabric/protos/peer"
)

type VoteChaincode struct {

}

type Vote struct {
	Username string `json:"username"`
	Votenum int `json:"votenum"`
}

func (t *VoteChaincode) Init(stub shim.ChaincodeStubInterface) peer.Response {
	return shim.Success(nil)
}

func (t *VoteChaincode) Invoke(stub shim.ChaincodeStubInterface) peer.Response {

	fn , args := stub.GetFunctionAndParameters()

	if fn == "voteUser" {
		return t.voteUser(stub,args)
	} else if fn == "getUserVote" {
		return t.getUserVote(stub,args)
	}

	return shim.Error("Invoke 调用方法有误！")
}

func (t *VoteChaincode) voteUser(stub shim.ChaincodeStubInterface , args []string) peer.Response{
	// 查询当前用户的票数，如果用户不存在则新添一条数据，如果存在则给票数加1
	fmt.Println("start voteUser")
	vote := Vote{}
	username := args[0]
	voteAsBytes, err := stub.GetState(username)

	if err != nil {
		shim.Error("voteUser 获取用户信息失败！")
	}

	if voteAsBytes != nil {
		err = json.Unmarshal(voteAsBytes, &vote)
		if err != nil {
			shim.Error(err.Error())
		}
		vote.Votenum += 1
	}else {
		vote = Vote{ Username: args[0], Votenum: 1} 
	}

	//将 Vote 对象 转为 JSON 对象
	voteJsonAsBytes, err := json.Marshal(vote)
	if err != nil {
		shim.Error(err.Error())
	}

	err = stub.PutState(username,voteJsonAsBytes)
	if err != nil {
		shim.Error("voteUser 写入账本失败！")
	}

	fmt.Println("end voteUser")
	return shim.Success(nil)
}

func (t *VoteChaincode) getUserVote(stub shim.ChaincodeStubInterface, args []string) peer.Response{

	fmt.Println("start getUserVote")
	// 获取所有用户的票数
	resultIterator, err := stub.GetStateByRange("","")
	if err != nil {
		return shim.Error("获取用户票数失败！")
	}
	defer resultIterator.Close()

	var buffer bytes.Buffer
	buffer.WriteString("[")

	isWritten := false

	for resultIterator.HasNext() {
		queryResult , err := resultIterator.Next()
		if err != nil {
			return shim.Error(err.Error())
		}

		if isWritten == true {
			buffer.WriteString(",")
		}

		buffer.WriteString(string(queryResult.Value))
		isWritten = true
	}

	buffer.WriteString("]")

	fmt.Printf("查询结果：\n%s\n",buffer.String())
	fmt.Println("end getUserVote")
	return shim.Success(buffer.Bytes())
}

func main(){
	err := shim.Start(new(VoteChaincode))
	if err != nil {
		fmt.Println("vote chaincode start err")
	}
}