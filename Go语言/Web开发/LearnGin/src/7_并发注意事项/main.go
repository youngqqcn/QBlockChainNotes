package  main

import (
	"github.com/gin-gonic/gin"
	"time"
	"log"
	"net/http"
)

/**
*作者: yqq
*日期: 2019/1/28  10:41
*描述:

	当在中间件或者处理程序中启动新的Goroutines时, 必须使用原始上下文的只读副本!!

*/

func main() {


	router := gin.Default()

	router.GET("/long_async", func(c *gin.Context) {

		c_cp := c.Copy()
		//c_cp := c

		ch := make(chan string, 1)
		go func()  {
			time.Sleep(6 * time.Second)
			log.Println("done...................... ", c_cp.Request.URL.Path)
			ch <- "hello--------------"
		}()
		c.String(http.StatusOK, <-ch)
	})

	router.GET("/long_sync", func(c *gin.Context) {
		time.Sleep(5 * time.Second)
		log.Println("Done.................")
	})

	router.Run(":8080")

}
