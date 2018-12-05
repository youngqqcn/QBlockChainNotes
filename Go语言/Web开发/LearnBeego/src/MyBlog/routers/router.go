package routers

import (
	"MyBlog/controllers"
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/context"
)

func init() {

	//设置过滤路由
	beego.InsertFilter("/MyBlog/*", beego.BeforeRouter, filterFunc)




    //beego.Router("/", &controllers.MainController{})
	beego.Router("/register", &controllers.RegisterController{} , "get:Get;post:Register")
    beego.Router("/", &controllers.LoginController{}, "get:Get;post:Login")

 //   beego.Router("/index", &controllers.IndexController{}, "get:Get;post:HandleSelectType")
	beego.Router("/MyBlog/index", &controllers.IndexController{}, "get:Get")

	beego.Router("/MyBlog/addArticle", &controllers.AddArticleController{}, "get:Get;post:AddArticle")
    beego.Router("/MyBlog/content", &controllers.ContentController{}, "get:Get")

    beego.Router("/MyBlog/update", &controllers.UpdateController{}, "get:Get;post:UpdateArticle")
	beego.Router("/MyBlog/delete", &controllers.UpdateController{}, "get:DeleteArticle")

    beego.Router("/MyBlog/addArticleType", &controllers.ArticleTypeController{}, "get:Get;post:AddArticleType")
	beego.Router("/MyBlog/deleteArticleType", &controllers.ArticleTypeController{}, "get:DeleteArticleType")

	beego.Router("/MyBlog/logout", &controllers.IndexController{}, "get:Logout")


}



var filterFunc = func(ctx *context.Context) {
	userName := ctx.Input.Session("username")
	if  userName == nil{
		ctx.Redirect(302, "/")
	}
}
