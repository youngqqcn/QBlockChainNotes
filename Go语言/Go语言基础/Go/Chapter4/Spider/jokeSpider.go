package main

import (
	"net/http"
	"io"
		"regexp"
	"fmt"
	"os"
	"strings"
	"strconv"
)

/**
*作者: yqq
*日期: 2018/11/30  16:56
*描述: 段子爬虫, 并发


爬取: http://duanziwang.com/category/经典段子/

//页面
第1页: http://duanziwang.com/category/%E7%BB%8F%E5%85%B8%E6%AE%B5%E5%AD%90/
第2页: http://duanziwang.com/category/%E7%BB%8F%E5%85%B8%E6%AE%B5%E5%AD%90/2/
第3页: http://duanziwang.com/category/%E7%BB%8F%E5%85%B8%E6%AE%B5%E5%AD%90/3/
...

//段子内容分析
	<h1 class="post-title"> 段子标题 </h1>
	<div class="post-content"> 段子内容 </div>
*/

var chCounter = make(chan int)

func JokeSpider(strURL string, strFileName string) (bOk bool, err error )  {

	defer func() {
		chCounter <- 1
	}()

	rsp, err := http.Get(strURL)
	if err != nil{
		bOk = false
		fmt.Println(err)
		return
	}
	defer rsp.Body.Close()

	buf := make([]byte , 1024 * 4)
	result := ""
	for {
		len := 0
		len, err = rsp.Body.Read(buf)
		if err != nil{
			if err == io.EOF{
				break
			}else{
				bOk = false
				fmt.Println(err)
				return
			}
		}

		//fmt.Printf(string(buf[:len]))
		result += string(buf[:len])
	}

	//正则表达式 : 获取段子标题
	reg  := regexp.MustCompile(`<h1 class="post-title".*?><a.*?>(?s:(.*?))</a></h1>`)
	matchesTitle := reg.FindAllStringSubmatch(result, -1)
	//for _, text := range matches{
	//	fmt.Println(text[1])
	//}


	//正则表达式  : 获取段子内容
	regCont := regexp.MustCompile(`<div .*?post-content.*?>(?s:.*?<p>)(?s:(.*?))</div>`)
	matchesCont := regCont.FindAllStringSubmatch(result, -1)
	//for _, text := range matches{
	//	fmt.Println(text[1])
	//}

	if len(matchesTitle) != len(matchesCont){
		err = fmt.Errorf("标题数和段子内容数, 不相等, 请确认")
		fmt.Println(err)
		return
	}

	jokeMap := make(map[string]string)
	for i := 0; i < len(matchesTitle); i++{

		jokeMap[matchesTitle[i][1]] = matchesCont[i][1] //放入map

		//fmt.Println(matchesTitle[i][1])
		//fmt.Println(matchesCont[i][1])
		//fmt.Println("======================")

	}


	//开始写文件
	fileOut, err := os.Create(strFileName)
	if err  != nil{
		fmt.Println(err)
		return
	}
	defer fileOut.Close()

	for strTile, strCont := range jokeMap{

		strCont = strings.Replace(strCont, "<p>", "", -1)
		strCont = strings.Replace(strCont, "</p>", "\n", -1)
		strCont = strings.Replace(strCont, "<br>", "\n", -1)


		fileOut.WriteString("        " + strTile + "\n\n")
		fileOut.WriteString(strCont + "\n\n---------\n\n")
	}
	fmt.Println("写入成功")



	bOk = true
	return
}



func main() {



	//exec.Command("del ./Chapter4/Spider/*.txt")

	nPageCount := 45
	for i := 1; i <= nPageCount; i++ {
		strURL := `http://duanziwang.com/category/%E7%BB%8F%E5%85%B8%E6%AE%B5%E5%AD%90/` + strconv.Itoa(i) + `/`
		strFileName := "./Chapter4/Spider/" + strconv.Itoa(i) + ".txt"
		go JokeSpider(strURL, strFileName)
	}

	for i := 1 ; i <= nPageCount; i++{
		 <- chCounter
		fmt.Println("已经下载了", i, "页")
	}

}
