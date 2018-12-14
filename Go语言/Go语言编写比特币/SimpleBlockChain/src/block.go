package main

import (
	"time"
	"bytes"
	"encoding/gob"
	"log"
	"crypto/sha256"
)

//区块类
type Block struct {
	TimeStamp 	int64 //时间戳
	//Data 		[]byte
	Transactions []*Transaction //交易的集合


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
func NewBlock(transactions []*Transaction, prevBlockhash []byte)  *Block {
	block := &Block{time.Now().Unix(),
	transactions,
	prevBlockhash,
	[]byte{},
	0}

	//工作量证明
	pow := NewProofOfWork(block)
	nonce, hash := pow.Run()  //开始挖矿
	block.Hash = hash[:]
	block.Nonce  = nonce


	return block
}


//创建创世区块

func NewGenesisBlock(coinbase *Transaction) *Block {

	return NewBlock([]*Transaction{coinbase}, []byte{})

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


//叠加交易数据, 计算hash
func (block *Block)HashTransactions() []byte  {

	var txHashes [][]byte
	var txHash[32]byte  //256bit


	for _, tx := range block.Transactions {
		txHashes = append(txHashes, tx.ID)
	}
	txHash = sha256.Sum256(bytes.Join(txHashes, []byte{}))


	return txHash[:]
}












