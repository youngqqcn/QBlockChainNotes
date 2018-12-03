package main

import (
	"regexp"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/12/3  15:16
*描述: 正则表达式

	1.通过正则表达式  验证是否匹配
	2.通过正则获取内容
*/



func main() {
	a := "I am learning Go language"

	re, _ := regexp.Compile("[a-z]{2,4}")

	//查找符合正则的第一个
	one := re.Find([]byte(a))
	fmt.Println("Find:", string(one))

	//查找符合正则的所有slice,n小于0表示返回全部符合的字符串，不然就是返回指定的长度
	all := re.FindAll([]byte(a), -1)
	fmt.Println("FindAll", all)

	//查找符合条件的index位置,开始位置和结束位置
	index := re.FindIndex([]byte(a))
	fmt.Println("FindIndex", index)

	//查找符合条件的所有的index位置，n同上
	allindex := re.FindAllIndex([]byte(a), -1)
	fmt.Println("FindAllIndex", allindex)

	re2, _ := regexp.Compile("am(.*)lang(.*)")

	//查找Submatch,返回数组，第一个元素是匹配的全部元素，第二个元素是第一个()里面的，第三个是第二个()里面的
	//下面的输出第一个元素是"am learning Go language"
	//第二个元素是" learning Go "，注意包含空格的输出
	//第三个元素是"uage"
	submatch := re2.FindSubmatch([]byte(a))
	fmt.Println("FindSubmatch", submatch)
	for _, v := range submatch {
		fmt.Println(string(v))
	}

	//定义和上面的FindIndex一样
	submatchindex := re2.FindSubmatchIndex([]byte(a))
	fmt.Println(submatchindex)

	//FindAllSubmatch,查找所有符合条件的子匹配
	submatchall := re2.FindAllSubmatch([]byte(a), -1)
	fmt.Println(submatchall)

	//FindAllSubmatchIndex,查找所有字匹配的index
	submatchallindex := re2.FindAllSubmatchIndex([]byte(a), -1)
	fmt.Println(submatchallindex)
}










/*
//Expand
func main() {
	src := []byte(`
		call hello alice
		hello bob
		call hello eve
	`)
	pat := regexp.MustCompile(`(?m)(call)\s+(?P<cmd>\w+)\s+(?P<arg>.+)\s*$`)
	res := []byte{}
	for _, s := range pat.FindAllSubmatchIndex(src, -1) {
		res = pat.Expand(res, []byte("$cmd('$arg')\n"), src, s)  //???
	}
	fmt.Println(string(res))
}

*/






/*
使用复杂的正则首先是Compile，它会解析正则表达式是否合法，
如果正确，那么就会返回一个Regexp，然后就可以利用返回的Regexp在任意的字符串上面执行需要的操作。


func Compile(expr string) (*Regexp, error)
func CompilePOSIX(expr string) (*Regexp, error)


//MustXXXXXXXXXXX 函数 如果匹配模式不满足正确的语法, 直接panic
func MustCompile(str string) *Regexp
func MustCompilePOSIX(str string) *Regexp
 */

 /*

func main() {
	resp, err := http.Get("http://www.baidu.com") //只支持 http, 不支持https
	if err != nil {
		fmt.Println("http get error.")
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("http read error")
		return
	}

	src := string(body)

	//将HTML标签全转换成小写
	re, _ := regexp.Compile("\\<[\\S\\s]+?\\>")
	src = re.ReplaceAllStringFunc(src, strings.ToLower)

	//去除STYLE
	re, _ = regexp.Compile("\\<style[\\S\\s]+?\\</style\\>")
	src = re.ReplaceAllString(src, "")

	//去除SCRIPT
	re, _ = regexp.Compile("\\<script[\\S\\s]+?\\</script\\>")
	src = re.ReplaceAllString(src, "")

	//去除所有尖括号内的HTML代码，并换成换行符
	re, _ = regexp.Compile("\\<[\\S\\s]+?\\>")
	src = re.ReplaceAllString(src, "\n")

	//去除连续的换行符
	re, _ = regexp.Compile("\\s{2,}")
	src = re.ReplaceAllString(src, "\n")

	fmt.Println(strings.TrimSpace(src))
}

*/



/*
//1.通过正则表达式  验证是否匹配,  例如:  验证ip地址是否合法
func main() {


	funcIsIP := func(strIp string) bool{
		bMatch, err := regexp.MatchString(`^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])(\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)){3}$`, strIp)
		if err != nil{
			panic(err)
		}
		return bMatch

	}

	fmt.Println( funcIsIP("192.168.1.1") ) //true
	fmt.Println( funcIsIP("www.168.1.1") ) //false
	fmt.Println( funcIsIP("192.168.999.1") ) //false
	fmt.Println( funcIsIP("10.168.234.255") ) //true
	fmt.Println( funcIsIP("255.255.255.255")) //false
	fmt.Println( funcIsIP("255.255.255.255.255")) //false

}
*/
