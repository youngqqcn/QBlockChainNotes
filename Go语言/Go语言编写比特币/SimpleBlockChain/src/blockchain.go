package main

import (
	"github.com/boltdb/bolt"
	"log"
	"fmt"
	"os"
	"encoding/hex"
)

const dbFile = "blockchain.db" //数据库文件名
const blockBucket  = "blocks"  //
const genesisCoinbaseData = "yqq"


type BlockChain struct {

	blocks [] *Block  //区块链

	tip []byte    //用于保存最后一个区块的 hash
	db *bolt.DB  //Bolt数据库

}

type  BlockChainIterator struct {
	currentHash []byte  //当前hash
	db *bolt.DB
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
func NewBlockChain(address string)  *BlockChain{


	if dbExists() == false{
		fmt.Println("数据库不存在, 创建一个")
		os.Exit(1)
	}

	var tip []byte   //存储区块链二进制数据
	db, err := bolt.Open(dbFile, 0600, nil) //打开数据库
	if err != nil{
		log.Panic(err)
	}

	err = db.Update(func(tx *bolt.Tx) error {
		bucket := tx.Bucket([]byte(blockBucket)) //从blockBucket表中取数据
		tip = bucket.Get([]byte("rearBlockHash")) //获取hash
		return nil
	})
	if err != nil{
		log.Panic(err)
	}

	bc := BlockChain{tip:tip, db:db}
	return &bc


}



//创建一个区块链数据库
func CreateBlockChain(address string  ) *BlockChain{
	if dbExists(){
		fmt.Println(" 数据库已经存在,无需创建")
		os.Exit(1)
	}

	var tip []byte   //存储区块链二进制数据
	db, err := bolt.Open(dbFile, 0600, nil) //打开数据库
	if err != nil{
		log.Panic(err)
	}

	err = db.Update(func(tx *bolt.Tx) error {

		cbtx := NewCoinBaseTX(address, genesisCoinbaseData) //创世区块事务交易
		genesis := NewGenesisBlock(cbtx)  //创建创世区块
		bucket, err := tx.CreateBucket([]byte(blockBucket))
		if err != nil{
			log.Panic(err)
		}

		err = bucket.Put(genesis.Hash, genesis.Serialize())
		if err != nil{
			log.Panic(err)
		}

		err = bucket.Put([]byte("rearBlockHash"), genesis.Hash)
		if err != nil{
			log.Panic(err)
		}

		return nil
	})




	bc := BlockChain{tip:tip, db:db}
	return &bc
}


//获取所有没有使用的交易
func (blockChain *BlockChain)FindUTXO(address string)[]TXOutput{

	var UTXOs []TXOutput

	unspentTransactions := blockChain.FindUnspentTransactions(address)

	for _, tx := range unspentTransactions{
		for _, out := range tx.Vout{
			if out.CanBeUnlockedWith(address){
				UTXOs = append(UTXOs, out)
			}
		}
	}

	return  UTXOs
}

func (blockChain *BlockChain)MineBlock(transactions []*Transaction){
	var lastHash []byte  //最后一个区块的hash

	err := blockChain.db.View(func(tx *bolt.Tx) error {
		bucket := tx.Bucket([]byte(blockBucket))
		lastHash = bucket.Get([]byte("rearBlockHash"))
		return nil
	})
	if err != nil{
		log.Panic(err)
	}

	newBlock := NewBlock(transactions, lastHash)
	err = blockChain.db.Update(func(tx *bolt.Tx) error {

		bucket := tx.Bucket([]byte(blockBucket))
		err := bucket.Put(newBlock.Hash, newBlock.Serialize()) //存入数据库
		if err != nil{
			log.Panic(err)
		}
		err  = bucket.Put([]byte("rearBlockHash"), newBlock.Hash)
		if err != nil{
			log.Panic(err)
		}

		blockChain.tip = newBlock.Hash
		return nil
	})
	if err != nil{
		log.Panic(err)
	}

}


//获取没有输出的交易列表
func (blockChain *BlockChain)FindUnspentTransactions(address string)[]Transaction{

	var unspentTXs []Transaction

	spentTXOS := make(map[string][]int) //开辟内存
	bcit := blockChain.Iterator()

	for{
		block := bcit.Next()

		for _, tx := range block.Transactions  {

			txID := hex.EncodeToString(tx.ID) //获取交易编号
		Output:
			for outindex, out := range tx.Vout  {
				if spentTXOS[txID] != nil{
					for _, spentOut := range spentTXOS[txID]{
						if spentOut == outindex{
							continue Output
						}
					}
				}

				if out.CanBeUnlockedWith(address){
					unspentTXs = append(unspentTXs, *tx)
				}


			}


			if tx.IsCoinBase() == false{
				for _, in := range tx.Vin{
					if in.CanUnlockOutputWith(address){ //是否可以锁定
						inTxID := hex.EncodeToString(in.Txid) //编码为字符串
						spentTXOS[inTxID] = append(spentTXOS[inTxID], in.Vout)

					}
				}
			}


		}

		if len(block.PrevBlockHash) == 0 { //遍历到创世区块
			break
		}
	}



	return unspentTXs
}


func (blockChain *BlockChain)FindSpendableOutputs(address string, amount int)(int , map[string][]int){

	unspentOutputs := make(map[string][]int)
	unspentTxs := blockChain.FindUnspentTransactions(address) //根据地址查找所有交易
	accumulate := 0

	Work:

		for _, tx := range unspentTxs {
			txID := hex.EncodeToString(tx.ID)
			for outindex, out := range tx.Vout{
				if out.CanBeUnlockedWith(address) && accumulate < amount{
					accumulate += out.Value
					unspentOutputs[txID] = append(unspentOutputs[txID], outindex) //序列叠加??

					if accumulate >= amount{
						break Work
					}

				}
			}

		}


	return accumulate, unspentOutputs
}

func dbExists()bool  {

	if _, err := os.Stat(dbFile); os.IsNotExist(err){
		return false
	}
	return true
}























