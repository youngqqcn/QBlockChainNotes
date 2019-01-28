package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
	"log"
)

/**
*作者: yqq
*日期: 2019/1/27  22:03
*描述:
	参考网址: https://www.jianshu.com/p/98965b3ff638
*/


//带参数的路由
func test1(router *gin.Engine)  {
	//访问: http://127.0.0.1:8080/user/yqq
	//返回: Hello yqq
	router.GET("/user/:name", func(c *gin.Context) {
		name := c.Param("name")
		c.String(http.StatusOK, "Hello %s", name)
	})

	//访问:http://127.0.0.1:8080/user/yqq/action1
	//返回: yqq is /action1
	router.GET("/user/:name/*action", func(c *gin.Context) {
		name := c.Param("name")
		action := c.Param("action")
		message := name + " is " + action
		c.String(http.StatusOK, message)
	})
	
}

func test2(router *gin.Engine)  {

	router.GET("/welcome", func(c *gin.Context) {
		firstname := c.DefaultQuery("firstname", "Guest") //如果没有firstname,则使用Guest作为fisrtname
		lastname := c.Query("lastname")

		c.String(http.StatusOK, "hello %s %s", firstname, lastname)
	})


	//POST   表单传参 (postman中使用 x-www-form-urlencoded)
	router.POST("/form_post", func(c *gin.Context) {

		user_agent := c.GetHeader("User-Agent")
		content_type := c.GetHeader("Content-Type")

		log.Println(user_agent)
		log.Println(content_type)


		message := c.PostForm("message")
		nick := c.DefaultPostForm("nick", "anonymous")

		c.JSON(http.StatusOK, gin.H{
			"status" : "posted",
			"message": message,
			"nick": nick,
		})
	})
}



func main() {

	router := gin.Default()
	test1(router)
	test2(router)


	router.Run(":8080")
}
