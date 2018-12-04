package controllers

import (
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/orm"
	"MyBlog/models"
)

type ContentController struct {
	beego.Controller
}

func (c *ContentController)Get()  {

	articleId, err := c.GetInt("id")
	if err != nil{
		beego.Info("获取文章id错误")
		return
	}

	//查找数据库
	o := orm.NewOrm()

	article := models.Article{}
	article.Id = articleId
	err = o.Read(&article)
	if err != nil{
		beego.Info("查找数据库失败")
		return
	}

	//article.ImgURL = article.ImgURL[1:]
	c.Data["article"] = article
	c.TplName = "content.html"
}
