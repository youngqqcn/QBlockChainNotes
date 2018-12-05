package main
//
//import (
//	_ "github.com/go-sql-driver/mysql"
//	"github.com/astaxie/beego/orm"
//	"log"
//	"fmt"
//)
//
///**
//*作者: yqq
//*日期: 2018/12/5  23:31
//*描述:
//*/
//// UserM2M table   用户表，与用户组表多对多关系
//type UserM2M struct {
//	Id         int  `orm:"auto"`
//	UserName   string
//	Groups     []*Group `orm:"rel(m2m)"` //多对多
//}
//// Group table 用户组表，与用户表多对多关系
//type Group struct {
//	Id        int `orm:"auto"`
//	GroupName string
//	Users     []*UserM2M `orm:"reverse(many)"` //反向多对多
//}
//
//func init()  {
//	orm.RegisterDataBase("default", "mysql", "root:dlj@/test2", 30)
//
//	// 需要在init中注册定义的model
//	orm.RegisterModel(new(UserM2M), new(Group)) //, new(Tag))
//
//	orm.RunSyncdb("default", false, true)
//}
//
//
////func main() {
////	o := orm.NewOrm()
////	u1 := UserM2M{UserName: "zhangszan"}
////	u2 := UserM2M{UserName: "lisi"}
////	g1 := Group{GroupName: "g1"}
////	g2 := Group{GroupName: "g2"}
////	//o.InsertMulti(2, []UserM2M{u1, u2})
////	o.InsertMulti(2, []UserM2M{u1, u2})
////	o.InsertMulti(2, []Group{g1, g2})
////	m2m := o.QueryM2M(&g1, "Users")
////	m2m.Add(&u1)
////	m2m.Add(&u1)
////
////	m2m2 := o.QueryM2M(&g2, "Users")
////	m2m2.Add(&u2)
////}
//
//func main() {
//	o := orm.NewOrm()
//	var u1  UserM2M
//	u1.UserName = "zhangsan"
//
//	var u2 UserM2M
//	u2.UserName =  "lisi"
//
//
//	var g1 Group
//	g1.GroupName = "group1"
//
//	var g2 Group
//	g2.GroupName = "group2"
//
//
//	//o.Insert(&u1)
//	//o.Insert(&u2)
//	//
//	//o.Insert(&g1)
//	//o.Insert(&g2)
//
//	rows, err := o.InsertMulti(2, []*UserM2M{&u1, &u2})
//	if err != nil{
//		log.Println(err)
//		return
//	}
//	fmt.Println("rows=", rows)
//
//	o.InsertMulti(2, []*Group{&g1, &g2})
//	if err != nil{
//		log.Println(err)
//		return
//	}
//	fmt.Println("rows=", rows)
//
//
//	m2m := o.QueryM2M(&g1, "Users")
//	m2m.Add(&u1)
//	m2m.Add(&u2)
//
//	m2m2 := o.QueryM2M(&g2, "Users")
//	m2m2.Add(&u2)
//}
