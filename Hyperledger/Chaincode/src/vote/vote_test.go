package main

import (
	"testing"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"fmt"
)

func checkInvoke(t *testing.T, stub *shim.MockStub, args [][]byte)  {

	res := stub.MockInvoke("1", args)
	if res.Status != shim.OK{
		fmt.Println("Invoke", "failed", string(res.Message))
		t.FailNow()
	}

}



func TestVote_Invoke(t  *testing.T)  {

	stub := shim.NewMockStub("vote_test", new(VoteChaincode))

	checkInvoke(t, stub, [][]byte{[]byte("voteUser"), []byte("yqq")})
	checkInvoke(t, stub, [][]byte{[]byte("voteUser"), []byte("yqq")})
	checkInvoke(t, stub, [][]byte{[]byte("voteUser"), []byte("Tom")})
	checkInvoke(t, stub, [][]byte{[]byte("voteUser"), []byte("Jack")})
	checkInvoke(t, stub, [][]byte{[]byte("voteUser"), []byte("Tom")})
	checkInvoke(t, stub, [][]byte{[]byte("voteUser"), []byte("yqq")})



	checkInvoke(t, stub, [][]byte{[]byte("getUserVote"), []byte("")})


}

