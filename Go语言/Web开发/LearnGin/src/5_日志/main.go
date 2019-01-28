package main

import (
	"os"
	"github.com/gin-gonic/gin"
	"io"
	"net/http"
	)

/**
*作者: yqq
*日期: 2019/1/27  23:18
*描述: 日志
*/


func main() {
	fileLog , _ := os.Create("gin.log")
	gin.DefaultWriter = io.MultiWriter(fileLog)

	router := gin.Default()
	router.GET("/ping", func(c *gin.Context) {
		//log.Println("============kkk=====")
		gin.DefaultWriter.Write([]byte("==============K\n=========="))
		c.String(http.StatusOK, "pong")
	})

	router.Run(":8080")
}
