package routers

import (
	"HelloBeego/controllers"
	"github.com/astaxie/beego"
)

func init() {
    beego.Router("/", &controllers.MainController{})
	beego.Router("/testgetpost", &controllers.TestGetPostController{}) //添加路由
	beego.Router("/createtable", &controllers.ORMComtroller{}) //ORM操作
	beego.Router("/register", &controllers.RegisterController{}) //用户注册相关
	beego.Router("/login", &controllers.LoginController{}, "get:Get;post:Login") //用户登录




}
