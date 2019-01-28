package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"log"
)

/**
*作者: yqq
*日期: 2019/1/27  23:29
*描述: 模型绑定和验证

绑定:对参数进行验证

Must Bind  :  如果绑定失败, 将直接返回400错误, 响应头设置为 text/plain; charset=utf-8
Should Bind :  如果绑定错误, 错误被返回, 有开发者自己处理
*/


type Login struct {
	Username string `form:"username" json:"username" binding:"required"`
	Password string `form:"password" json:"password" binding:"required"`
}




func main() {

	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	router.POST("/loginJSON", func(c *gin.Context) {
		log.Println("=================1")
		var jsonArgs Login
		if err := c.ShouldBindJSON(&jsonArgs); err == nil{
			c.JSON(http.StatusOK, gin.H{"status":"ok..........."})
		}else{
			c.JSON(http.StatusBadRequest, gin.H{"error" : err.Error()})
		}
	})


	router.POST("/loginForm", func(c *gin.Context) {
		log.Println("=======================2")
		var form Login
		if err := c.ShouldBind(&form); err == nil{

			if form.Username == "yqq" && form.Password == "1234"{
				c.JSON(http.StatusOK, gin.H{"status" : "logined........."})
			}else{
				c.JSON(http.StatusOK, gin.H{"error" : err.Error()})
			}
		}
	})


	router.GET("/secureJSON", func(c *gin.Context) {
		c.SecureJSON(http.StatusOK, "secure..........................")
	})



	router.Run(":8080")


}
