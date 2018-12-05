package controllers

import (
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/orm"
	"MyBlog/models"
	"fmt"
		"path"
	"strconv"
)

type UpdateController struct {

	beego.Controller

}

func (c *UpdateController)Get()  {

	//获取文章id
	id , err := c.GetInt("id")
	if err != nil{
		beego.Info("获取文章id 失败")
		return
	}

	//根据文章id , 获取文字信息
	o := orm.NewOrm()
	article := models.Article{}
	beego.Info("artiId:", id)
	article.Id = id

	err = o.Read(&article)
	if err != nil{
		beego.Info("查询id失败")
		fmt.Println()
	}

	c.Data["article"] = article
	c.TplName = "update.html"

}

func (c *UpdateController)UpdateArticle()  {

	id , err:= c.GetInt("id")
	if err != nil{
		beego.Info("获取文章id失败")
		return
	}

	//获取文章信息
	article := models.Article{}
	article.Id = id

	o := orm.NewOrm()
	err = o.Read(&article)
	if err != nil{
		beego.Info("根据文章id,查询数据库错误")
		return
	}
	//更新文章数据
	article.Title = c.GetString("articleName")
	article.Content = c.GetString("content")

	//保存图片
	imgFile, header, err := c.GetFile("uploadname")
	if err != nil{
		beego.Info("GetFile错误", err)
		return
	}
	defer imgFile.Close()

	imgEx := path.Ext(header.Filename)
	if imgEx != ".jpg" && imgEx != ".png" && imgEx != ".JPG" && imgEx != ".PNG"{
		beego.Info("图片格式不合法, 请检查")
		return
	}

	if header.Size > 50 * 1024 * 1024 {
		beego.Info("图片太大")
		return
	}

	fileName := "./static/upload/" + header.Filename
	err = c.SaveToFile("uploadname", fileName)
	if err != nil{
		beego.Info("savetofile err")
		return
	}
	article.ImgURL = "static/upload/" + header.Filename


	//更新数据库
	rows, err := o.Update(&article)
	if err != nil{
		beego.Info("update err")
		return
	}
	beego.Info("更新了 ", rows, "行数据")


	//调到文章内容页面
	c.Redirect("/MyBlog/content?id=" + strconv.Itoa(article.Id), 302)
	//c.Ctx.WriteString("文章id是: " + strconv.Itoa(id))
}

//删除文章
func (c *UpdateController)DeleteArticle()  {

	//获取文章id
	id, err := c.GetInt("id")
	if err != nil{
		beego.Info("获取文字id错误")
		return
	}

	//删除数据库中的文章数据
	o := orm.NewOrm()

	article := models.Article{Id:id}
	//err = o.Read(&article)
	rows, err := o.Delete(&article, "Id")
	if err != nil{
		beego.Info(err)
		return
	}
	beego.Info("删除了 ", rows, " 行数据")


	c.Redirect("/MyBlog/index", 302)
}
