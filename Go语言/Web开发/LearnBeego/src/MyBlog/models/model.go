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

	Articles []*Article `orm:"rel(m2m)"`
}


type Article struct {
	Id  int  `orm:"pk;auto"`
	Title	string `orm:"size(64);unique"`
	Content	string
	CreateTime time.Time  `orm:"auto_now;type(datetime)"`
	ReadCount  int  `orm:"default(0)"`
	Type string  `orm:"null"`
	ImgURL string `orm:"null"`

	ArticleType *ArticleType `orm:"rel(fk)"`
	Users []*User  `orm:"reverse(many)"`
}

type ArticleType struct {
	Id int `orm:"pk;auto"`
	Type string `orm:"size(32);unique"`

	Articles []*Article `orm:"reverse(many)"`
}




func init()  {

	err := orm.RegisterDataBase("default", "mysql", "root:dlj@/test")
	if err != nil{
		panic(err)
	}

	orm.RegisterModel(&User{}, &Article{}, &ArticleType{})

	orm.RunSyncdb("default", false, true)
}

