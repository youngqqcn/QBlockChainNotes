package main

import (
	"encoding/xml"
	"fmt"
	"os"
)

/**
*作者: yqq
*日期: 2018/12/3  14:08
*描述: xml 操作
*/


//输出xml文件

type Servers struct {
	XMLName xml.Name `xml:"servers"`
	Version string `xml:"version,attr"`
	Svs []server `xml:"server"`
}



type server struct {
	ServerName string `xml:"serverName"`
	ServerIP string `xml:"serverIP"`
}




func main() {

	v := &Servers{Version:"1"}
	v.Svs = append(v.Svs, server{"Shanghai_VPN", "127.0.0.1"})
	v.Svs = append(v.Svs, server{"Shenzhen_VPN", "189.34.22.1"})

	output, err := xml.MarshalIndent(v, "  ", "    ")
	if err != nil{
		fmt.Printf("error, %v\n", err)
	}
	os.Stdout.Write([]byte(xml.Header))
	fmt.Printf("===========\n\n")
	os.Stdout.Write(output)

}







//解析xml文件
/*
type RecurlyServers struct {
	XMLName xml.Name `xml:"servers"`
	Version string `xml:"version,attr"`
	Svs []server `xml:"server"`
	Description string `xml:",innerxml"`
}



type server struct {
	XMLName xml.Name  `xml:"server"`
	ServerName string `xml:"serverName"`
	ServerIP string `xml:"serverIP"`
}




func main() {

	xmlFile, err := os.Open("./Chapter7/test.xml")
	if err != nil{
		fmt.Println(err)
		return
	}
	defer	xmlFile.Close()

	data, err := ioutil.ReadAll(xmlFile)
	if err != nil{
		fmt.Println(err)
		return
	}

	v := RecurlyServers{}
	err = xml.Unmarshal(data, &v)
	if err != nil{
		fmt.Println(err)
		return
	}

	fmt.Println(v)
}
*/