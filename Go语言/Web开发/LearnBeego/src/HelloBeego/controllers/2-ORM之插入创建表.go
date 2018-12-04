package controllers

import (
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/orm"
	"HelloBeego/models"
)

type ORMComtroller struct {

	beego.Controller

}

func (c *ORMComtroller) InsertData()  {


	//插入数据
	/*
	o := orm.NewOrm()
	id, err := o.Insert(&models.User{5, "yqq", "54321"})
	if err != nil{
		//fmt.Println(err)
		//fmt.Println("创建失败")
		beego.Info("创建失败")
		return
	}
	fmt.Println(id)
	*/

	/*
	//查询数据
	o := orm.NewOrm()
	user := models.User{}
	//user.Id = 5
	//err := o.Read(&user)
	user.Name = "yqq"
	err := o.Read(&user, "name")
	if err != nil{
		beego.Info("查询失败")
		return
	}
	beego.Info("查询成功")
	beego.Info(user.Name, user.Pwd)
	*/


	/*
	//更新数据
	o := orm.NewOrm()
	user := models.User{}
	user.Id = 5
	if err := o.Read(&user); err != nil{
		beego.Info("查询失败")
		return
	}

	user.Name = "Tom"
	user.Pwd = "IamTom"
	rows, err := o.Update(&user)
	if err != nil{
		beego.Info("更新失败")
		return
	}
	beego.Info("更新数据成功", rows)
	*/


	//删除数据
	o := orm.NewOrm()
	user := models.User{}
	user.Id = 5

	rows, err := o.Delete(&user, "id")
	if err != nil{
		beego.Info("删除失败")
		return
	}
	beego.Info("删除成功 ", rows)
}

func ( c *ORMComtroller) Post()  {
	c.InsertData()
	c.Get()

}


func (c *ORMComtroller) Get() {
	c.TplName = "2-ORM之创建数据表.html"
}