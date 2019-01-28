package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

/**
*作者: yqq
*日期: 2019/1/27  21:44
*描述: 路由分组
*/



func main() {

	gin.SetMode(gin.ReleaseMode)

	router := gin.Default()

	//group1 : v1

	v1 := router.Group("/v1")
	{
		v1.POST("/login", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"message":"v1/login ok...........",
			})
		})
	}

	v2 := router.Group("/v2")
	{
		v2.POST("/login", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"message":"v2/login ok...........",
			})
		})
	}


	router.Run(":8080")
}
