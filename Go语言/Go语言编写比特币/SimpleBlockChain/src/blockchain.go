package main

import (
	"github.com/boltdb/bolt"
	"log"
	"fmt"
)

const dbFile = "blockchain.db" //数据库文件名
const blockBucket  = "blocks"  //


type BlockChain struct {

	blocks [] *Block  //区块链

	tip []byte    //用于保存最后一个区块的 hash
	db *bolt.DB  //Bolt数据库

}

type  BlockChainIterator struct {
	currentHash []byte  //当前hash
	db *bolt.DB
}

//增加一个区块
func (block *BlockChain)AddBlock( data string)  {

	var rearBlockHash []byte //最后一个区块的hash


	err := block.db.View(func(tx *bolt.Tx) error {
		block := tx.Bucket([]byte(blockBucket))
		rearBlockHash = block.Get([]byte("rearBlockHash")) //取得最后一个区块的hash
		return nil
	})
	if err != nil{
		log.Panic(err)
	}

	newBlock := NewBlock(data, rearBlockHash)
	err = block.db.Update(func(tx *bolt.Tx) error {
		bucket  := tx.Bucket([]byte(blockBucket))
		err := bucket.Put(newBlock.Hash, newBlock.Serialize()) //压入数据
		if err != nil{
			log.Panic(err)
		}

		err = bucket.Put([]byte("rearBlockHash"), newBlock.Hash)  //更新最后一个块hash的值
		if err != nil{
			log.Panic(err)
		}

		block.tip = newBlock.Hash   //最后一个区块的hash
		return nil
	})



}

//迭代器
func (bc *BlockChain)Iterator() *BlockChainIterator  {
	bcit := &BlockChainIterator{bc.tip, bc.db}
	return bcit
}

//下一个区块
func (it *BlockChainIterator)Next() *Block{
	var block *Block
	err := it.db.View(func(tx *bolt.Tx) error {
		bucket := tx.Bucket([]byte(blockBucket))
		encodeBlock := bucket.Get(it.currentHash) //从数据库获取对象的二进制数据(序列化的)
		block = DeserializeBlock(encodeBlock) //解码
		return nil
	})
	if err != nil{
		log.Panic(err)
	}

	it.currentHash = block.PrevBlockHash
	return block
}

//新建区块链
func NewBlockChain()  *BlockChain{

	var tip []byte   //存储区块链二进制数据
	db, err := bolt.Open(dbFile, 0600, nil) //打开数据库
	if err != nil{
		log.Panic(err)
	}

	//处理数据更新
	err = db.Update(func(tx *bolt.Tx) error {
		bucket := tx.Bucket([]byte(blockBucket)) //从blockBucket表中取数据
		if bucket == nil {
			fmt.Println("当前数据库没有区块链, 创建一个新的链")
			//return nil

			//创建数据库
			genesis := NewGenesisBlock()
			bucket, err := tx.CreateBucket([]byte(blockBucket))
			if err != nil {
				log.Panic(err) //
			}

			//存储数据
			err = bucket.Put(genesis.Hash, genesis.Serialize())
			if err != nil {
				log.Panic(err) //
			}

			err = bucket.Put([]byte("rearBlockHash"), genesis.Hash)  //添加一个 key为 "rearBlockHash"的k-v对
			if err != nil {
				log.Panic(err) //
			}

			tip = genesis.Hash
		}else {
			tip = bucket.Get([]byte("rearBlockHash")) //获取hash

		}


		return nil
	})
	if err != nil{
		log.Panic(err)
	}

	bc := BlockChain{tip:tip, db:db}
	return &bc


}



