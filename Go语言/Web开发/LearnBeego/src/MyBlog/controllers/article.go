package controllers

/*

//记忆:  6 1 2 3 4 5
//
//go语言  时间格式化
const (
	date        = "2006-01-05"
	shortdate   = "06-01-05"
	times       = "15:04:05"
	shorttime   = "15:04"
	datetime    = "2006-01-02 15:04:05"
	newdatetime = "2006/01/02 15~04~05"
	newtime     = "15~04~05"
)

 */


import (
	"github.com/astaxie/beego"
	"MyBlog/models"
	"github.com/astaxie/beego/orm"
	"path"
	"time"
	"strings"
)





type AddArticleController struct {
	beego.Controller
}

func (c *AddArticleController) Get() {

	o := orm.NewOrm()
	var articleTypes  []models.ArticleType
	rows, err := o.QueryTable(&models.ArticleType{}).All(&articleTypes)
	if err != nil{
		beego.Info("查询文章类型失败")
		return
	}
	beego.Info("文章类型个数:", rows)

	c.Data["articleTypes"] = articleTypes

	c.TplName = "add.html"
}


func (c *AddArticleController) AddArticle() {

	articleName := c.GetString("articleName")
	articleCont :=  c.GetString("content")

	beego.Info(articleCont)
	beego.Info(articleName)


	//上传图片
	file, header, err := c.GetFile("uploadname")
	defer file.Close()
	if err != nil{
		beego.Info("GetFile失败")
		return
	}

	imgEx := path.Ext(header.Filename)
	if imgEx != ".jpg" && imgEx != ".png" {
		beego.Info("图片格式错误")
		return
	}
	if header.Size > 50000000{
		beego.Info("图片大于50M, 错误")
		return
	}

	fileName := time.Now().Format("2006-01-02-15-04-05") + imgEx

	err = c.SaveToFile("uploadname", "static/upload/"+ fileName )
	if err != nil{
	 	beego.Info(err)
		return
	}


	//校验数据
	if len(articleName) == 0 || len(articleCont) == 0{
		beego.Info("数据为空")
		return
	}

	articleType := c.GetString("selectType")
	articleType = strings.Trim(articleType, " ")
	if len(articleType) == 0{
		beego.Info("文章类型为空")
		return
	}
	beego.Info("获取到文章类型是:", articleType)

	//写入数据库
	o := orm.NewOrm()

	articleTypeStruct := models.ArticleType{}
	articleTypeStruct.Type = articleType
	err = o.Read(&articleTypeStruct, "Type")
	if err != nil{
		beego.Info("查询文章类型表, 发生错误")
		return
	}


	article :=  models.Article{}
	article.ArticleType = &articleTypeStruct
	article.Type = articleType
	article.Content = articleCont
	article.Title = articleName
	article.ImgURL  = "static/upload/"  + fileName

	 _, err = o.Insert(&article)
	 if err != nil{
	 	beego.Info(err)
		 return
	 }
	c.Redirect("/MyBlog/index", 302)
}

