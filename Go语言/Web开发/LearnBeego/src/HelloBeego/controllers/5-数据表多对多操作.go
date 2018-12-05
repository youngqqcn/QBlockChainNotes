package controllers

import (
	"github.com/astaxie/beego"
	"github.com/astaxie/beego/orm"
	"HelloBeego/models"
)

type M2MTableController struct {
	
	beego.Controller
	
}

//插入
func (c *M2MTableController)M2MInsert()  {

	o := orm.NewOrm()
	stu1 := models.Stu{Name:"yqq"}
	stu2 := models.Stu{Name:"Tom"}

	sub1 := models.Subject{Name:"高数"}
	sub2 := models.Subject{Name:"算法"}

	//o.InsertMulti(2, []models.Stu{stu1, stu2})
	//o.InsertMulti(2, []models.Subject{sub1, sub2})


	m2mstu1 := o.QueryM2M(&stu1, "Subject")
	m2mstu2 := o.QueryM2M(&stu2, "Subject")

	m2mstu1.Add(&sub1)
	m2mstu1.Add(&sub2)

	m2mstu2.Add(&sub1)


	c.Ctx.WriteString("插入")
	
}

//查询
func (c *M2MTableController)M2MQuery()  {
	c.Ctx.WriteString("查询")

}


