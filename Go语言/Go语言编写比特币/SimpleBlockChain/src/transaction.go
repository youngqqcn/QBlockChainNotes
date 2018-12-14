package main

import (
	"bytes"
	"encoding/gob"
	"log"
	"crypto/sha256"
	"fmt"
	"encoding/hex"
)

const subsidy = 10 	//挖矿的奖励

//输入
type TXInput struct {
	Txid []byte   //交易id
	Vout int   //交易索引
	ScriptSig string  //用户定义的钱包地址
}

//检查地址是否启动事务
func (input *TXInput)CanUnlockOutputWith(unlockingData string) bool  {
	return input.ScriptSig == unlockingData
}

//输出
type TXOutput struct {
	Value int           //
	ScriptPubKey string
}

func (output *TXOutput)CanBeUnlockedWith(unlockingData string) bool  {
	return output.ScriptPubKey == unlockingData  //
}

//交易类
type Transaction struct {
	ID []byte
	Vin  []TXInput    //交易输入
	Vout []TXOutput   //交易输出
}



//检查交易事务是否是coinbase, 是否是挖矿得来的
func (tx *Transaction)IsCoinBase() bool  {
	return len(tx.Vin ) == 1 && len(tx.Vin[0].Txid) == 0 && tx.Vin[0].Vout == -1
}

func (tx *Transaction)SetID()  {
	var encoded bytes.Buffer
	var hash[32] byte
	enc := gob.NewEncoder(&encoded)
	err := enc.Encode(tx)
	if err != nil{
		log.Panic(err)
	}

	hash = sha256.Sum256(encoded.Bytes())
	tx.ID = hash[:]

}

//挖矿交易
func NewCoinBaseTX(to, data string) *Transaction {
	if data == ""{
		data = fmt.Sprintf("挖矿奖励给%s", to)
	}

	txin := TXInput{[]byte{}, -1, data}
	txout := TXOutput{subsidy, to}
	tx := Transaction{nil, []TXInput{txin}, []TXOutput{txout}}
	return &tx
}


//转账交易
func NewUTXOTransaction(from , to string, amount int, bc *BlockChain) *Transaction  {
	var inputs []TXInput
	var outputs []TXOutput

	acc , validOutputs := bc.FindSpendableOutputs(from, amount)
	if acc < amount{
		log.Panic("交易金额不足")
	}


	for txid, outs := range validOutputs{
		txID, err := hex.DecodeString(txid)
		if err != nil{
			log.Panic(err)
		}

		for _, out := range outs {
			input := TXInput{txID, out, from} //输入的交易
			inputs = append(inputs, input ) //输出的交易
		}
	}


	//交易叠加
	outputs = append(outputs, TXOutput{amount, to})
	if acc > amount{

		outputs = append(outputs, TXOutput{acc - amount, from})
	}

	tx := Transaction{nil, inputs, outputs}
	tx.SetID()
	return &tx
}



















