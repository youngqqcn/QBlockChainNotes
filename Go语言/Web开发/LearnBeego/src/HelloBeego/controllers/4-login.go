package controllers

import (
	"github.com/astaxie/beego"
	"strings"
	"github.com/astaxie/beego/orm"
	"HelloBeego/models"
)

type LoginController struct {

	beego.Controller

}

func (c *LoginController)Get()  {

	c.TplName = "4-用户登录界面.html"

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

	c.Ctx.WriteString("登录成功")

}


