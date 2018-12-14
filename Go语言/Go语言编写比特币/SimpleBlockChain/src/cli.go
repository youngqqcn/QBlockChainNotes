package main



import (
"fmt"
"os"
"strconv"
	"flag"
	"log"
)

/**
*作者: yqq
*日期: 2018/12/14  10:33
*描述:
*/


//命令行接口
type CLI struct {
	blockChain  *BlockChain
}



//打印用法
func (cli *CLI)printUsage()  {

	fmt.Println("用法如下:")
	fmt.Println("addblock   向区块链增加块")
	fmt.Println("showchain  显示区块链")


}


func (cli *CLI)validateBlock()  {

	if len(os.Args) < 2{
		cli.printUsage() //打印用法
		os.Exit(1)
	}

}

func (cli *CLI)addBlock(data string)  {
	cli.blockChain.AddBlock(data) //增加区块
	fmt.Println("区块增加成功")
}



//显示区块链
func (cli *CLI)showBlockChain()  {
	bcit := cli.blockChain.Iterator()

	for{
		block := bcit.Next() //取得下一个区块

		fmt.Printf("上一块区块Hash:%x\n", block.PrevBlockHash)
		fmt.Printf("交易数据: %s\n", block.Data)
		fmt.Printf("当前区块的Hash: %x\n", block.Hash)

		pow := NewProofOfWork(block)
		fmt.Printf("pow %s\n", strconv.FormatBool(pow.Validate()))

		fmt.Println("===============================")

		if len(block.PrevBlockHash) == 0{ //创世区块
			break
		}

	}

}

func (cli *CLI)Run()  {

	//校验
	cli.validateArgs()


}

func (cli *CLI)validateArgs()  {
	addblockcmd := flag.NewFlagSet("addblock", flag.ExitOnError)
	showchaincmd := flag.NewFlagSet("addblock", flag.ExitOnError)

	addBlockData := addblockcmd.String("data", "", "addBlockData data")
	switch os.Args[1] {
	case "addblock":
		err := addblockcmd.Parse(os.Args[2:])
		if err != nil{
			log.Panic(err)
		}

	case "showchain":
		err := showchaincmd.Parse(os.Args[2:])
		if err != nil{
			log.Panic(err)
		}

	default:
		cli.printUsage()
		os.Exit(1)
	}

	if addblockcmd.Parsed(){
		if *addBlockData == ""{
			addblockcmd.Usage()
			os.Exit(1)

		}else{
			cli.addBlock(*addBlockData)
		}
	}

	if showchaincmd.Parsed(){
		cli.showBlockChain()
	}

}





