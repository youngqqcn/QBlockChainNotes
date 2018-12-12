package main

import (
	"fmt"
	"strconv"
)

/**
*作者: yqq
*日期: 2018/12/12  13:56
*描述: 实现简单区块链
*/


func main() {

	//fmt.Println("hello")


	blockchain := NewBlockChain()

	blockchain.AddBlock("yqq --> qqy  +10 ")
	blockchain.AddBlock("yqq --> qqy  -10 ")
	blockchain.AddBlock("yqq --> qqy  +10 ")
	blockchain.AddBlock("yqq --> qqy  -10 ")

	for _, block := range blockchain.blocks{

		fmt.Printf("上一块区块Hash:%x\n", block.PrevBlockHash)
		fmt.Printf("交易数据: %s\n", block.Data)
		fmt.Printf("当前区块的Hash: %x\n", block.Hash)

		pow := NewProofOfWork(block)
		fmt.Printf("pow %s\n", strconv.FormatBool(pow.Validate()))


		fmt.Println("===============================")

	}

}

/*
000000e2c2c707e24d23110fbfb687021da6b22d985a6e53bac1087d9bcc449c


000000aece8f5d530b8b3c24e80dc7d8c55db4fc131e315f73e14699000c9373


0000002e94242e5ddbbd31fb2b0b2180b607d0c2df9668b17f83a4fa2de6bbd0


000000f7126c1c43f69d92164c3f0fe29aa039b58432106a6503dcbbbc9143c4


0000002bd686a7aaa889cc3f7e4e516470a5d3585e89a84a256076e4f5796142


上一块区块Hash:
交易数据: yqq
当前区块的Hash: 000000e2c2c707e24d23110fbfb687021da6b22d985a6e53bac1087d9bcc449c
pow true
===============================
上一块区块Hash:000000e2c2c707e24d23110fbfb687021da6b22d985a6e53bac1087d9bcc449c
交易数据: yqq --> qqy  +10
当前区块的Hash: 000000aece8f5d530b8b3c24e80dc7d8c55db4fc131e315f73e14699000c9373
pow true
===============================
上一块区块Hash:000000aece8f5d530b8b3c24e80dc7d8c55db4fc131e315f73e14699000c9373
交易数据: yqq --> qqy  -10
当前区块的Hash: 0000002e94242e5ddbbd31fb2b0b2180b607d0c2df9668b17f83a4fa2de6bbd0
pow true
===============================
上一块区块Hash:0000002e94242e5ddbbd31fb2b0b2180b607d0c2df9668b17f83a4fa2de6bbd0
交易数据: yqq --> qqy  +10
当前区块的Hash: 000000f7126c1c43f69d92164c3f0fe29aa039b58432106a6503dcbbbc9143c4
pow true
===============================
上一块区块Hash:000000f7126c1c43f69d92164c3f0fe29aa039b58432106a6503dcbbbc9143c4
交易数据: yqq --> qqy  -10
当前区块的Hash: 0000002bd686a7aaa889cc3f7e4e516470a5d3585e89a84a256076e4f5796142
pow true
===============================
 */

