package main

import (
	"time"
	"bytes"
	"encoding/gob"
	"log"
)

//区块类
type Block struct {
	TimeStamp 	int64 //时间戳
	Data 		[]byte
	PrevBlockHash []byte
	Hash 		[]byte //当前区块Hash

	Nonce int //工作量正面
}

/*
//设置区块的hash
func (this *Block)SetHash()  {

	timestamp := []byte(strconv.FormatInt(this.TimeStamp, 10))
	headers := bytes.Join([][]byte{this.PrevBlockHash, this.Data, timestamp}, []byte{})
	hash := sha256.Sum256(headers)
	this.Hash = hash[:]
}
*/


//创建新的区块
func NewBlock(data string, prevBlockhash []byte)  *Block {
	block := &Block{time.Now().Unix(), []byte(data), prevBlockhash, []byte{}, 0}
	//block.SetHash()

	//工作量证明
	pow := NewProofOfWork(block)
	nonce, hash := pow.Run()  //开始挖矿
	block.Hash = hash[:]
	block.Nonce  = nonce


	return block
}


//创建创世区块

func NewGenesisBlock() *Block {

	return NewBlock("yqq", []byte{})

}

func (block *Block)Serialize() []byte  {

	var result bytes.Buffer
	encoder := gob.NewEncoder(&result)
	err := encoder.Encode(block)  //序列化
	if err != nil{
		log.Panic(err)
	}

	return result.Bytes()
}

func DeserializeBlock (data []byte) *Block {

	var block Block
	decoder := gob.NewDecoder(bytes.NewReader(data)) //反序列化
	err := decoder.Decode(&block)
	if err != nil{
		log.Panic(err)
	}

	return &block
}

















