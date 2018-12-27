package main

import (
	"fmt"
	"testing"
	"github.com/hyperledger/fabric/core/chaincode/shim"
)

func checkInvoke(t *testing.T, stub *shim.MockStub, args [][]byte) {
	res := stub.MockInvoke("1",args)
	if res.Status != shim.OK {
		fmt.Println("Invoke", "failed", string(res.Message))
		t.FailNow()
	}
}


func TestExample02_Invoke(t *testing.T) {
	scc := new(VoteChaincode)
	stub := shim.NewMockStub("ex02", scc)

	checkInvoke(t,stub,[][]byte{[]byte("voteUser"), []byte("xiaoming")})

	checkInvoke(t,stub,[][]byte{[]byte("voteUser"), []byte("xiaoming")})
	
	checkInvoke(t,stub,[][]byte{[]byte("voteUser"), []byte("xiaowang")})
	checkInvoke(t,stub,[][]byte{[]byte("voteUser"), []byte("xiaowang")})
	checkInvoke(t,stub,[][]byte{[]byte("voteUser"), []byte("xiaowang")})

	checkInvoke(t,stub,[][]byte{[]byte("getUserVote"), []byte("")})


}