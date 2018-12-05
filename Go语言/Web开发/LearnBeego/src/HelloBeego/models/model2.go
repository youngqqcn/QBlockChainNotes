package models

import (
	_ "github.com/go-sql-driver/mysql"
	)

/**
*作者: yqq
*日期: 2018/12/5  22:23
*描述: 熟悉 数据表的 多对多关系
		1.插入
		2.查询


参考: https://zhangwenbing.com/blog/other/15818
https://zhangwenbing.com/blog/golang
*/



//学生
type Stu struct {
	Id int `orm:"auto"`
	Name string `orm:"unique"`
	Department string
	Email string

	Subject  []*Subject `orm:"rel(m2m)"`   //课程
}

//课程
type Subject struct {
	Id int  `orm:"auto"`
	Name string `orm:"unique"`
	Information string
	Stu []*Stu  `orm:"reverse(many)"`  //反向多对多
}



//model下只能有一个 init 函数??
//
//func init()  {
//
//	//err :=  orm.RegisterDataBase("m2m", "mysql", "root:dlj@/test")
//	//if err != nil{
//	//	panic(err)
//	//}
//	//orm.RegisterModel(&Stu{}, &Subject{})
//	//orm.RunSyncdb("m2m", false, true)
//}




