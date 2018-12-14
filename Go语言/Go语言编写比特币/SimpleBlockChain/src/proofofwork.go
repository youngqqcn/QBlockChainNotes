package main

import (
	"math"
	"math/big"
	"bytes"
	"fmt"
	"crypto/sha256"
)

var (
	maxNonce = math.MaxInt64
)


const targetBits = 8*2     //对比的位数


type ProofOfWork struct {
	block *Block  //区块
	target *big.Int             //存储哈希对比的整数
}


//创建一个工作量正面的挖矿对象o
func NewProofOfWork(block *Block) *ProofOfWork {

	target := big.NewInt(1  )
	target.Lsh(target, uint(256 - targetBits)) //数据转换

	pow := &ProofOfWork{block, target}
	return  pow
}


//准备数据进行计算
func (pow *ProofOfWork)prepareData(nonce int)[]byte  {

	data  := bytes.Join(
		[][]byte{
			pow.block.PrevBlockHash,  //上一个区块hash
			pow.block.HashTransactions(),   //当前数据
			IntToHex(pow.block.TimeStamp), //时间十六进制
			IntToHex(int64(targetBits)), //位数, 十六进制

			IntToHex(int64(nonce)), //保存工作量证明,  通过变化这个数, 使data的hash值小于目标值
		},
		[]byte{}, )


	return data
}

//挖矿
func (pow *ProofOfWork)Run() (int, []byte ){

	var hashInt big.Int
	var hash [32]byte
	nonce := 0

	//fmt.Printf("当前挖矿计算的区块数据%s", pow.block.Data)

	for nonce < maxNonce{
		data := pow.prepareData(nonce)
		hash = sha256.Sum256(data) //计算出hash
		fmt.Printf("\r%x", hash)

		hashInt.SetBytes(hash[:]) //获取要对比的数据

		//找一个数(data的hash值) : 小于  1 << (256-targetBits)
		if hashInt.Cmp(pow.target) == -1{
			break
		}else{
			nonce ++
		}
	}

	fmt.Println("\n\n")
	return  nonce, hash[:]   //
}



//校验挖矿是否成功
func(pow *ProofOfWork) Validate() bool{

	var hashInt big.Int
	data := pow.prepareData(pow.block.Nonce)
	hash := sha256.Sum256(data)
	hashInt.SetBytes(hash[:])
	isValid := (hashInt.Cmp(pow.target) == -1)


	return isValid

}







