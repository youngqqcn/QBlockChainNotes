package controllers

import (
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/orm"
	"MyBlog/models"
	"math"
	"strconv"
)

type IndexController struct {

	beego.Controller

}

func (c *IndexController)Get()  {

	//if c.GetSession("username") == nil{
	//	c.Redirect("/", 302)
	//	return
	//}



	var articles []models.Article

	o := orm.NewOrm()
	qs := o.QueryTable("article")
	//articleCount := 0
	var err error
	var articleCount int64
	if c.GetString("selectType") != ""{
		articleCount, err = qs.RelatedSel("ArticleType").Filter("ArticleType__Type", c.GetString("selectType")).Count()
		beego.Info(c.GetString("selectType"), "类型的新闻一共", articleCount," 篇")
	}else{
		articleCount, err = qs.RelatedSel("ArticleType").Count() // 多表查询
		if err != nil{
			beego.Info("QueryTable err")
			return
		}
	}

	curPageIndex, err := c.GetInt("pageIndex")
	if err != nil{
		curPageIndex = 1
	}

	pageSize := 1
	pageCount :=  math.Ceil( float64(articleCount) / float64(pageSize) )




	//第一页, 取消"上一页"
	if 1 == curPageIndex{
		c.Data["isFirstPage"] = true
	}else{
		c.Data["isFirstPage"] = false
	}
	//最后一页, 取消"下一页"
	if int(pageCount) == curPageIndex{
		c.Data["isLastestPage"] = true
	}else{
		c.Data["isLastestPage"] = false
	}


	var curPageArticles []models.Article
	//RelatedSel  关联查询
	tmpRows ,err := qs.Limit(pageSize/*size*/, pageSize *(curPageIndex - 1)/*startIndex*/).RelatedSel("ArticleType").All(&curPageArticles)
	if err != nil{
		//有些文章因为历史原因没有类型
		tmpRows ,err = qs.Limit(pageSize/*size*/, pageSize *(curPageIndex - 1)/*startIndex*/).All(&curPageArticles)
		if err != nil{
			beego.Info("qs.Limit err")
			return
		}
	}
	beego.Info("tmpRows=", tmpRows)



	for i, article := range articles{
		beego.Info(i, article.Title, article.Content, article.CreateTime)
		//c.Ctx.WriteString(string(strconv.Itoa(i) + " " +  article.Title + " " + article.Content + " " + article.CreateTime.Format("2006-01-02")))
	}

	var articleTypes  []models.ArticleType
	rows, err := o.QueryTable(&models.ArticleType{}).All(&articleTypes)
	if err != nil{
		beego.Info("查询文章类型失败")
		return
	}
	beego.Info("文章类型个数:", rows)


	////////////////////{ 实现根据文章类型获取文章列表 }/////////////////////////////
	strType :=  c.GetString("select")
	beego.Info(strType)

	if strType != ""{

		articleType := models.ArticleType{}
		articleType.Type = strType
		err = o.Read(&articleType, "Type")
		if err != nil{
			beego.Info("查询数据库, 未找到文章类型先关数据")
			return
		}

		//核心代码
		var oneTypeArticles  []models.Article
		qs.Limit(pageSize/*size*/, pageSize *(curPageIndex - 1)).RelatedSel("ArticleType").Filter("ArticleType__Type", strType).All(&oneTypeArticles)

		curPageArticles = oneTypeArticles
	}
	/////////////////////////////////////////////////



	c.Data["selectType"] = strType
	c.Data["articleTypes"] = articleTypes
	c.Data["articleCount"] = articleCount
	c.Data["articles"] = curPageArticles
	c.Data["pageCount"] = pageCount
	c.Data["curPageIndex"] = curPageIndex


	c.TplName = "index.html"
}


func (c *IndexController)Logout()  {

	c.DelSession("username")

	c.Redirect("/", 302)

}

//
//func (c *IndexController)HandleSelectType()  {
//
//	///////////////////////////////////////////
//	//从数据库中获取文章的相关信息
//
//	var articles []models.Article
//
//	o := orm.NewOrm()
//	qs := o.QueryTable("article")
//	//articleCount,err := qs.All(&articles)
//	articleCount,err := qs.RelatedSel("ArticleType").Count() // 多表查询
//	if err != nil{
//		beego.Info("QueryTable err")
//		return
//	}
//
//	curPageIndex, err := c.GetInt("pageIndex")
//	if err != nil{
//		curPageIndex = 1
//	}
//
//	pageSize := 1
//	pageCount :=  math.Ceil( float64(articleCount) / float64(pageSize) )
//
//	//第一页, 取消"上一页"
//	if 1 == curPageIndex{
//		c.Data["isFirstPage"] = true
//	}else{
//		c.Data["isFirstPage"] = false
//	}
//	//最后一页, 取消"下一页"
//	if int(pageCount) == curPageIndex{
//		c.Data["isLastestPage"] = true
//	}else{
//		c.Data["isLastestPage"] = false
//	}
//
//	var curPageArticles []models.Article
//	//RelatedSel  关联查询
//	tmpRows ,err := qs.Limit(pageSize/*size*/, pageSize *(curPageIndex - 1)/*startIndex*/).RelatedSel("ArticleType").All(&curPageArticles)
//	if err != nil{
//		//有些文章因为历史原因没有类型
//		tmpRows ,err = qs.Limit(pageSize/*size*/, pageSize *(curPageIndex - 1)/*startIndex*/).All(&curPageArticles)
//		if err != nil{
//			beego.Info("qs.Limit err")
//			return
//		}
//	}
//	beego.Info("tmpRows=", tmpRows)
//
//	for i, article := range articles{
//		beego.Info(i, article.Title, article.Content, article.CreateTime)
//		//c.Ctx.WriteString(string(strconv.Itoa(i) + " " +  article.Title + " " + article.Content + " " + article.CreateTime.Format("2006-01-02")))
//	}
//
//	var articleTypes  []models.ArticleType
//	rows, err := o.QueryTable(&models.ArticleType{}).All(&articleTypes)
//	if err != nil{
//		beego.Info("查询文章类型失败")
//		return
//	}
//	beego.Info("文章类型个数:", rows)
//
//
//
//	////////////////////{ 实现根据文章类型获取文章列表 }/////////////////////////////
//	strType :=  c.GetString("select")
//	beego.Info(strType)
//
//	articleType := models.ArticleType{}
//	articleType.Type = strType
//	err = o.Read(&articleType, "Type")
//	if err != nil{
//		beego.Info("查询数据库, 未找到文章类型先关数据")
//		return
//	}
//
//	//核心代码
//	var oneTypeArticles  []models.Article
//	qs.Limit(pageSize/*size*/, pageSize *(curPageIndex - 1)).RelatedSel("ArticleType").Filter("ArticleType__Type", strType).All(&oneTypeArticles)
//
//	/////////////////////////////////////////////////
//
//	c.Data["articles"] = articleType.Articles
//	c.Data["selectType"] = articleType
//	c.Data["articleTypes"] = articleTypes
//	c.Data["articleCount"] = articleCount
//	c.Data["articles"] = oneTypeArticles //curPageArticles
//	c.Data["pageCount"] = pageCount
//	c.Data["curPageIndex"] = curPageIndex
//
//	c.TplName = "index.html"
//
//}



func GetPrePageIndex(curPageIndex interface{}) string  {

	if index,ok := curPageIndex.(int); ok{
		return strconv.Itoa( index - 1 )
	}else if strIndex, ok := curPageIndex.(string); ok{

		index, err := strconv.Atoi(strIndex)
		if err != nil{
			beego.Info("页码转换错误")
		}
		return strconv.Itoa( index - 1)
	}else{
	}

	return "0"
}


func GetNextPageIndex(curPageIndex interface{}) string  {

	if index,ok := curPageIndex.(int); ok{
		return strconv.Itoa( index + 1 )
	}else if strIndex, ok := curPageIndex.(string); ok{

		index, err := strconv.Atoi(strIndex)
		if err != nil{
			beego.Info("页码转换错误")
		}
		return strconv.Itoa( index + 1)
	}else{
	}

	return "0"
}




