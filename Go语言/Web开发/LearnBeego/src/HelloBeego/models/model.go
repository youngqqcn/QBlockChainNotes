package models

import (
	_ "github.com/go-sql-driver/mysql"
	"github.com/astaxie/beego/orm"
	)

type User struct {
	
	Id int
	Name string 
	Pwd  string
	
}

func init()  {

	err :=  orm.RegisterDataBase("default", "mysql", "root:dlj@/test")
	if err != nil{
		panic(err)
	}
	orm.RegisterModel(&User{}, &Subject{}, &Stu{})
	orm.RunSyncdb("default", false, true)

	
}
