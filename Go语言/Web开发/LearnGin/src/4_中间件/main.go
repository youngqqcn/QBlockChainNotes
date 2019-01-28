package main

import (
	"github.com/gin-gonic/gin"
	"fmt"
	"log"
)

/**
*作者: yqq
*日期: 2019/1/27  22:45
*描述: 中间件
*/

//gin.Default() 默认是加载了一些框架内置的中间件的，而 gin.New() 则没有，根据需要自己手动加载中间件。

//可以通过中间件, 实现API认证



func main() {

	r := gin.New()

	r.Use(gin.Logger())

	r.Use(gin.Recovery())

	r.GET("/benmark",  MyBenchLogger(), func(c *gin.Context) {
		log.Println("ennnnnnnnnnd")
	})


	r.Run(":8080")

}

func MyBenchLogger() gin.HandlerFunc {

	return func(c *gin.Context) {
		log.Println("111111111111111111")
		fmt.Println("before middleware")
		c.Set("requet", "client_request")
		c.Next()
		fmt.Println("after middleware")
	}

}
