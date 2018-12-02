package main

import (
	"github.com/astaxie/beego/orm"
	_ "github.com/go-sql-driver/mysql"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/12/2  19:28
*描述:
	Beego orm 库进行 ORM开发

*/

type User struct {
	Id int
	Name string  `orm:"size(100)"`
}






func init()  {
	orm.RegisterDataBase("default", "mysql", "root:dlj@/test", 30)

	orm.RegisterModel(new(User))

	orm.RunSyncdb("default", false, true)

}


func main() {

	o := orm.NewOrm()

	user := User{Name:"slene"}

	id, err := o.Insert(&user)
	fmt.Printf("ID:%d, ERR:%v\n", id, err)

	user.Name = "yqq"
	num, err := o.Update(&user)
	fmt.Printf("NUM: %d, ERR: %v\n", num, err)

	u := User{Id:user.Id}
	err = o.Read(&u)
	fmt.Printf("ERR:%v\n", err)

	num, err = o.Delete(&u)
	fmt.Printf("NUM:%d ERR:%v\n", num, err)

}
