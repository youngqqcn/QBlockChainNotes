package main

import (
	_ "MyBlog/routers"
	"github.com/astaxie/beego"
	"MyBlog/controllers"
)

func main() {


	beego.AddFuncMap("GetPrePageIndex", controllers.GetPrePageIndex)
	beego.AddFuncMap("GetNextPageIndex", controllers.GetNextPageIndex)
	beego.Run()
}

