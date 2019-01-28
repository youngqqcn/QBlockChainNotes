package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

/**
*作者: yqq
*日期: 2019/1/27  15:53
*描述: gin 框架学习    HelloWorld
*/



func setupRouter() *gin.Engine {

	r  := gin.Default()

	//r.GET("/", func(c *gin.Context) {
	//	c.String(http.StatusOK, "index")
	//})

	r.GET("/ping", func(c *gin.Context) {
		c.String(http.StatusOK, "Pong")
	})



	//接收Json

	type CallData struct {
		Method string  `json:"Method"`
		Args [3]interface{} `json:"Args"`
	}


	r.POST("/api", func(c *gin.Context) {

		var callData CallData
		if err := c.ShouldBindJSON(&callData); err == nil{
			c.JSON(http.StatusOK, gin.H{"message" : "ok..............."})
		}else{
			c.JSON(http.StatusOK, gin.H{
				"message" : "error...............",
				"error": err.Error(),
			})
		}

	})


	return r
}



func main() {
	gin.SetMode(gin.ReleaseMode)
	r := setupRouter()
	r.Run()
}