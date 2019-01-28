package main

import (
	"github.com/gin-gonic/gin"
	)

/**
*作者: yqq
*日期: 2019/1/28  11:00
*描述:  httptest
*/

func setupRouter() *gin.Engine  {

	r := gin.Default()
	r.GET("/ping", func(c *gin.Context) {
		c.String(200, "pong")
	})

	return r
}



func main() {

	r := setupRouter()
	r.Run(":8080")

}
