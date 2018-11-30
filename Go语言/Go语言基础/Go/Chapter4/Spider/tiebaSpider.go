package main

import (
	"net/http"
	"fmt"
	"os"
	"io"
	"strconv"
	)

/**
*作者: yqq
*日期: 2018/11/30  16:37
*描述: 百度贴吧爬虫
*/

func Spider(strUrl string, fileName string) (bOk bool) {
	rsp, err := http.Get(strUrl)
	if err != nil{
		fmt.Println(err)
		return
	}
	defer rsp.Body.Close()

	fileOut , err := os.Create(fileName )
	if err != nil{
		fmt.Println(err)
		return
	}
	defer fileOut.Close()

	buf := make([]byte, 1024 * 4)
	for{
		len, err := rsp.Body.Read(buf)
		if err != nil{
			if err == io.EOF{
				break
			}else{
				fmt.Println(err)
			}
		}
		fileOut.Write(buf[:len]) //读了多少写多少
	}

	bOk = true
	return
}



func main() {
 	strURL := `https://tieba.baidu.com/p/5861330529?pn=`
 	for i := 1; i <= 10; i ++{
 		strURL = strURL + strconv.Itoa(i)

 		strFileName :=   strconv.Itoa(i) + ".html"
 		 if   Spider(strURL, strFileName) {
 		 	fmt.Println(strFileName, "下载成功")
		 }else {
			 fmt.Println(strFileName, "下载失败")
		 }
	}

}
