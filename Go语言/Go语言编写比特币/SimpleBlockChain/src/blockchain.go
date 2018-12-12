package main




type BlockChain struct {

	blocks [] *Block  //区块链

}

func (blockchain *BlockChain )AddBlock( data string)  {

	preBlock  := blockchain.blocks[len(blockchain.blocks) - 1]

	newBlock := NewBlock(data, preBlock.Hash)
	blockchain.blocks = append(blockchain.blocks, newBlock)
}



func NewBlockChain()  *BlockChain {

	return &BlockChain{[]*Block{NewGenesisBlock()}}
}
