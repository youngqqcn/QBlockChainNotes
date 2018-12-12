package main

import (
	"math/big"
	"fmt"
)



func main()  {

	target := big.NewInt(1  )
	target.Lsh(target, uint(256 - 24)) //数据转换

	fmt.Printf("%x\n", target)

}

