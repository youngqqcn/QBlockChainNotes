package main



import (
"fmt"
"os"
"flag"
	"log"
	"strconv"
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

func (cli *CLI)createBlockChain(address string)  {

	bc := CreateBlockChain(address)
	bc.db.Close()

	fmt.Println("创建成功", address)

}

func (cli *CLI)getBalance(address string)  {
	bc := NewBlockChain(address)
	defer bc.db.Close()

	balance := 0
	UTXOs := bc.FindUTXO(address)
	for _, out := range UTXOs{
		balance += out.Value
	}

	fmt.Printf("查询的金额如下:%s 用于 %d 大洋\n", address, balance)

}







//打印用法
func (cli *CLI)printUsage()  {

	fmt.Println("用法如下:")
	fmt.Println("getbalance -address: 根据地址查询金额")
	fmt.Println("createblockchain -address :  根据地址创建区块链")
	fmt.Println("send -from addrFrom -to addTo -amount Amount    转账")
	fmt.Println("showchain  显示区块链")


}


func (cli *CLI)validateBlock()  {

	if len(os.Args) < 2{
		cli.printUsage() //打印用法
		os.Exit(1)
	}

}

func (cli *CLI)addBlock(data string)  {
	//cli.blockChain.AddBlock(data) //增加区块
	fmt.Println("区块增加成功")
}

func (cli *CLI)send(from , to string , amount int)  {
	bc := NewBlockChain(from)
	defer bc.db.Close()

	tx := NewUTXOTransaction(from, to, amount, bc)
	bc.MineBlock([]*Transaction{tx})
	fmt.Println("交易成功")

}


//显示区块链
func (cli *CLI)showBlockChain()  {

	bc := NewBlockChain("")
	defer bc.db.Close()

	bcit := bc.Iterator()
	for{
		block := bcit.Next()
		if block == nil{
			break
		}
		fmt.Println("===============================================")
		fmt.Printf("上一块哈希: %x\n", block.PrevBlockHash)
		fmt.Printf("当前哈希: %x\n", block.Hash)
		pow := NewProofOfWork(block)

		fmt.Printf("pow %s\n", strconv.FormatBool(pow.Validate()) )

		if len(block.PrevBlockHash) == 0{ //创世区块
			break
		}
	}
}

func (cli *CLI)run()  {

	//校验

	if len(os.Args) < 2{
		cli.printUsage()
		return
	}

	cli.validateArgs()


}

func (cli *CLI)validateArgs()  {





	getbalancecmd := flag.NewFlagSet("getbalance", flag.ExitOnError)
	createblockchiancmd := flag.NewFlagSet("createblockchain", flag.ExitOnError)
	sendcmd := flag.NewFlagSet("send", flag.ExitOnError)
	showchaincmd := flag.NewFlagSet("showchain", flag.ExitOnError)


	getbalanceaddress := getbalancecmd.String("address", "", "查询地址")
	createblockaddress := createblockchiancmd.String("address", "", "区块地址")
	sendfrom := sendcmd.String("from", "", "谁给的")
	sendto := sendcmd.String("to", "", "给谁的")
	sendamount := sendcmd.Int("amount", -1, "金额")



	switch os.Args[1] {

	case "getbalance":
		err := getbalancecmd.Parse(os.Args[2:])
		if err != nil{
			log.Panic(err)
		}
	case "createblockchain":
		err := createblockchiancmd.Parse(os.Args[2:])
		if err != nil{
			log.Panic(err)
		}

	case "send":
		err := sendcmd.Parse(os.Args[2:])
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



	if getbalancecmd.Parsed(){
		if *getbalanceaddress == ""{
			getbalancecmd.Usage()
			os.Exit(1)
		}
		cli.getBalance(*getbalanceaddress)
	}

	if createblockchiancmd.Parsed(){
		if *createblockaddress == ""{
			createblockchiancmd.Usage()
			os.Exit(1)
		}
		cli.createBlockChain(*createblockaddress) //
	}

	if sendcmd.Parsed(){
		if *sendfrom == "" || *sendto == "" || *sendamount <= 0{
			sendcmd.Usage()
			os.Exit(1)
		}

		cli.send(*sendfrom, *sendto, *sendamount)
	}



	if showchaincmd.Parsed(){
		cli.showBlockChain()
	}

}





