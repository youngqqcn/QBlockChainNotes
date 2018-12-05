package controllers

import (
	"github.com/astaxie/beego"
	"strings"
	"github.com/astaxie/beego/orm"
	"MyBlog/models"
	"time"
)



type LoginController struct {

	beego.Controller

}

func (c *LoginController)Get()  {

	username := c.Ctx.GetCookie("username")
	if username != "" {
		c.Data["username"] = username
		c.Data["checked"] = "checked"
	}else{
		c.Data["username"] = ""
		c.Data["checked"] = ""
	}


	c.TplName = "login.html"

}



//处理登录
func (c *LoginController)Login()  {

	//获取用户数据
	username := c.GetString("username")
	password := c.GetString("password")

	username = strings.Trim(username, " ")
	password = strings.Trim(password, " ")

	if 0 == len(username) || 0 == len(password){
		beego.Info("数据为空")
		return
	}

	//查数据库
	o := orm.NewOrm()

	user := models.User{Name:username}
	if err := o.Read(&user, "Name"); err != nil{
		beego.Info("查询数据库失败")
		c.Ctx.WriteString("查询数据库失败")
		return
	}
	if user.Pwd != password{
		beego.Info(password, user.Pwd)
		beego.Info("密码不正确")
		c.Ctx.WriteString("密码不正确")
		return
	}

	beego.Info("密码是:", user.Pwd)



	isChecked := c.GetString("rememberName")
	beego.Info("rememberName = ", isChecked)
	if isChecked == "on"{
		c.Ctx.SetCookie("username", username, time.Second * 60 * 60)
	}else{
		c.Ctx.SetCookie("username", username, -1 )

	}


	c.SetSession("username", username)


	//c.Ctx.WriteString("登录成功")
	c.Redirect("/MyBlog/index", 302)

}


