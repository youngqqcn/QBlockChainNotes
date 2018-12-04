package routers

import (
	"MyBlog/controllers"
	"github.com/astaxie/beego"
)

func init() {
    beego.Router("/", &controllers.MainController{})
	beego.Router("/register", &controllers.RegisterController{} , "get:Get;post:Register")
    beego.Router("/login", &controllers.LoginController{}, "get:Get;post:Login")
    beego.Router("/index", &controllers.IndexController{})
	beego.Router("/addArticle", &controllers.AddArticleController{}, "get:Get;post:AddArticle")
    beego.Router("/content", &controllers.ContentController{}, "get:Get")

    beego.Router("/update", &controllers.UpdateController{}, "get:Get;post:UpdateArticle")

}
