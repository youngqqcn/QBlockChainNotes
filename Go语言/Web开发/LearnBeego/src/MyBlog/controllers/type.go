package controllers

import (
	"github.com/astaxie/beego"
	"strings"
	"github.com/astaxie/beego/orm"
	"MyBlog/models"
)

type ArticleTypeController struct {

	beego.Controller

}

func (c *ArticleTypeController)Get()  {

	o := orm.NewOrm()

	var types []models.ArticleType
	rows, err := o.QueryTable(&models.ArticleType{}).All(&types)
	if err != nil{
		beego.Info("查询文章类型表失败")
		c.TplName = "addType.html"
		return
	}
	beego.Info(rows)


	c.Data["articleTypes"] = types
	c.TplName = "addType.html"
}

func (c *ArticleTypeController)AddArticleType()  {

	typeName := c.GetString("typeName")
	typeName = strings.Trim(typeName, " ")
	if len(typeName) == 0{
		c.Redirect("/MyBlog/addArticleType", 302)
		return
	}

	o := orm.NewOrm()
	_, err := o.Insert(&models.ArticleType{Type:typeName})
	if err != nil{
		beego.Info("添加分类:插入数据库错误")
		c.Redirect("/MyBlog/addArticleType", 302)
		return
	}
	c.Redirect("/MyBlog/addArticleType", 302)
}

func (c *ArticleTypeController)DeleteArticleType()  {

	id , err:= c.GetInt("id")
	if err != nil{
		c.Redirect("/MyBlog/addArticleType", 302)
		return
	}

	articleType := models.ArticleType{Id:id}

	o := orm.NewOrm()
	rows, err := o.Delete(&articleType, "Id")
	if err != nil{
		beego.Info("删除失败")
		c.Redirect("/MyBlog/addArticleType", 302)
		return
	}
	beego.Info("删除了:", rows, "行")

	c.Redirect("/MyBlog/addArticleType", 302)
}