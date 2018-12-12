package main

import (
	"crypto/sha256"
	"strconv"
	"fmt"
	"time"
)

func main()  {

	startTime := time.Now()
	time.Sleep(3 * time.Second)
	for i := 0; i <100000000000000000; i++{

		data := sha256.Sum256([]byte(strconv.Itoa(i)))
		fmt.Printf("%10d, %x\n", i, data)
		if string(data[len(data) -  2 : ]) == "00"{
			fmt.Printf("挖矿成功, 耗时%f 秒\n", time.Since(startTime).Seconds())
			break
		}
	}
}
