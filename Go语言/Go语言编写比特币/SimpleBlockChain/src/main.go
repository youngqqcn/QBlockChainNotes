package main
/**
*作者: yqq
*日期: 2018/12/14  10:50
*描述:
*/

func main() {

	block := NewBlockChain()  //创建区块链
	defer block.db.Close()
	cli := CLI{block} //创建命令行
	cli.Run()
}
