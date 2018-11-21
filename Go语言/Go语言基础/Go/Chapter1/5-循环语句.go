package main

import (
	"fmt"
	"math/rand"
	"time"
)

/**
*作者: yqq
*日期: 2018/11/21  18:25
*描述: 循环语句

	for
	range

*/

func main() {

	var i, sum int

	for i = 1; i < 100; i++{
		sum += i
	}
	fmt.Println("sum=", sum)



	////////////////////
	//string/array/slice/map 都支持 range

	s := "golang"
	for index := range s{
		fmt.Printf("s[%d]-->%c\n", index,  s[index])
	}

	///////////////////

LABEL_AGAIN:
	for i , sum:= 10, 0; i < 100  ; i++  {
		if sum > 99 {
			fmt.Println("sum=", sum)
			break
		}
		if (i & 1) == 0{ //跳过偶数
			continue
		}
		sum += i
	}


	///////////

	rand.Seed(time.Now().UnixNano())
	if 1 == rand.Int() & 1{
		goto LABEL_AGAIN
	}





}
