package models
import (
	_ "github.com/go-sql-driver/mysql"
	"github.com/astaxie/beego/orm"
	"time"
)


type User struct {

	Id int
	Name string `orm:"unique"`
	Pwd  string
}

type Article struct {
	Id  int  `orm:"pk;auto"`
	Title	string `orm:"size(64);unique"`
	Content	string
	CreateTime time.Time  `orm:"auto_now;type(datetime)"`
	ReadCount  int  `orm:"default(0)"`
	Type string  `orm:"null"`
	ImgURL string `orm:"null"`
}




func init()  {

	err := orm.RegisterDataBase("default", "mysql", "root:dlj@/test")
	if err != nil{
		panic(err)
	}

	orm.RegisterModel(&User{}, &Article{})

	orm.RunSyncdb("default", false, true)
}

