package controllers

import (
	"github.com/astaxie/beego"
	"time"
)



//继承  beego.Controller
type TestGetPostController struct {
	beego.Controller
}


func (c *TestGetPostController) Get() {
	c.Data["time"] = time.Now().String()
	c.TplName = "1-处理get和post请求.html"
}