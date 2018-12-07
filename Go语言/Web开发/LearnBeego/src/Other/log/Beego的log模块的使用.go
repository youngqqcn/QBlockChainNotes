package main

import "github.com/astaxie/beego/logs"

/**
*作者: yqq
*日期: 2018/12/7  9:47
*描述: Beego 的log模块使用
*/

func main() {

	log := logs.NewLogger(/*设置chan的大小*/)

	//所有的日志会输出到test.log
	log.SetLogger(logs.AdapterFile/**/, `{"filename":"test.log"}`)

	//所有的日志会输出到test.log
	//按照不同的日志, 进行分类输出到不同文件
	//log.SetLogger(logs.AdapterMultiFile/**/, `{"filename":"test", "separate":["emergency", "alert", "critical", "error", "warning", "notice", "info", "debug"]}`)
	logs.Info("this is a  debug info" ) //输出到控制台
	log.Info("info.....................") //输出到设置的文件中
	log.Debug("debug info...............")
	log.Warning("warning................")
	log.Error("error...................")
	log.Alert("alert...................")
	log.Emergency("ermergency....................")
	log.Notice("notice................")
	log.Critical("critical....................")
	log.Async(0x354) //设置异步

}