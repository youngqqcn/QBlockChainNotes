package controllers

import (
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/orm"
	"MyBlog/models"
	)

type IndexController struct {

	beego.Controller

}

func (c *IndexController)Get()  {

	//从数据库中获取文章的相关信息

	var articles []models.Article

	o := orm.NewOrm()
	_, err := o.QueryTable("article").All(&articles)
	if err != nil{
		beego.Info("QueryTable err")
		return
	}

	for i, article := range articles{
		beego.Info(i, article.Title, article.Content, article.CreateTime)
		//c.Ctx.WriteString(string(strconv.Itoa(i) + " " +  article.Title + " " + article.Content + " " + article.CreateTime.Format("2006-01-02")))
	}

	c.Data["articles"] = articles
	c.TplName = "index.html"
}


