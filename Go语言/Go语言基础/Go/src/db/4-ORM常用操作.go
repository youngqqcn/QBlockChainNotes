package main

import (
	"time"
	_ "github.com/go-sql-driver/mysql"   //初始化 mysql驱动
	"github.com/astaxie/beego/orm"
	"fmt"
)

/**
*作者: yqq
*日期: 2018/12/2  20:41
*描述: beego orm库   增删改查   操作


	这里简单了解了 Beego框架的ORM库,  后期再深入学习


*/

type Userinfo struct {
	//Id      int    //ok, 默认是主键
	//注意, 如果主键命名不是Id,则需要加上标签,显式说明它是主键,否则会报错 `needs a primary key field`
	Uid      int   `orm:"column(uid);pk"`
	//Uid      int   `PK`  //error,这个PK代表啥意思????

	Username string
	DepartName string
	Created  time.Time
}

type User4 struct{
	Id int
	Name string
	Profile *Profile  `orm:"rel(one)"`
	Post []*Post `orm:"reverse(many)"`

}

type Profile struct {
	Id int
	Age int16
	User *User4 `orm:"reverse(one)"`
}

type Post struct {
	Id int         `orm:"auto"`
	Title string    `orm:"size(100)"`
	User *User4 `orm:"rel(fk)"`
	//Tags []*Tag `orm:"rel(m2m)"`
}

//type Tag struct{
//	Id int
//	Name string
//	Posts []*Post `orm:"reverse(many)"`
//
//}




func init()  {
	orm.RegisterDataBase("default", "mysql", "root:dlj@/test", 30)

	// 需要在init中注册定义的model
	orm.RegisterModel(new(Userinfo), new(User4), new(Profile), new(Post))//, new(Tag))

	orm.RunSyncdb("default", false, true)

}



//查询数据
//func main()  {
//
//	o := orm.NewOrm()
//	//var user User
//	user := User4{Id: 1}
//	err := o.Read(&user)
//
//	if err == orm.ErrNoRows {
//		fmt.Println("查询不到")
//	} else if err == orm.ErrMissPK {
//		fmt.Println("找不到主键")
//	} else {
//		fmt.Println(user.Id, user.Name)
//	}
//}


// 更新数据
//func main()  {
//	o := orm.NewOrm()
//	user := User4{Id: 1}
//	if o.Read(&user) == nil {
//		user.Name = "MyName"
//		if num, err := o.Update(&user); err == nil {
//			fmt.Println(num)
//		}
//	}
//
//}


//插入数据
//func main() {
//	o := orm.NewOrm()
//
//	var user User4
//	user.Name = "yqq"
//	user.Profile = &Profile{Id:2}
//
//	id, err := o.Insert(&user)
//	if err != nil{
//		fmt.Println(err)
//		return
//	}
//	fmt.Println(id)
//
//}

//删除数据
//func main()  {
//	o := orm.NewOrm()
//	if num, err := o.Delete(&User4{Id: 1}); err == nil {
//		fmt.Println(num)
//	}
//
//}



// 关联查询(未成功)
//func main()  {
//
//	o := orm.NewOrm()
//
//	//type Post struct {
//	//	Id    int    `orm:"auto"`
//	//	Title string `orm:"size(100)"`
//	//	User  *User  `orm:"rel(fk)"`
//	//}
//
//	var posts []*Post
//	qs := o.QueryTable("post")
//	num, err := qs.Filter("User4__Name", "Tom").All(&posts) //error
//	if err != nil{
//		fmt.Println(err)
//		return
//	}
//	fmt.Println(num)
//}




////使用原生 sql
//func main()  {
//	o := orm.NewOrm()
//	r := o.Raw("UPDATE user4 SET name = ? WHERE name = ?", "Jaaaaaack", "yqq", )
//
//	//var r orm.RawSeter
//	var users []User4
//	num, err := r.QueryRows(&users) //执行sql语句
//	if err != nil{
//		fmt.Println(err)
//		return
//	}
//	fmt.Println(num)
//
//}


/*
mysql> select * from user4;
+----+-----------+------------+
| id | name      | profile_id |
+----+-----------+------------+
|  1 | hooooook  |          6 |
|  2 | Jaaaaaack |          2 |
|  9 | yqq       |         99 |
| 22 | Hulu      |        939 |
| 55 | Guizi     |        245 |
+----+-----------+------------+
 */
//复杂的原生 sql
func main()  {
	var o orm.Ormer
	var rs orm.RawSeter
	var users  []User4
	o = orm.NewOrm()
	rs = o.Raw("SELECT * FROM user4 "+
		"WHERE  Id> ? "+
		"ORDER BY Id DESC "+
		"LIMIT 100", "10")
	num, err := rs.QueryRows(&users)
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println(num)

		//打印出来users
		for _, user := range users{
			fmt.Println(user.Id, user.Name)
		}
	}

	return

}

