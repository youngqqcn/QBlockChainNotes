package main

import (
	"database/sql"
	_ "github.com/go-sql-driver/mysql"     //注册 mysql驱动
	"fmt"
)


/*

CREATE TABLE `userinfo` (
	`uid` INT(10) NOT NULL AUTO_INCREMENT,
	`username` VARCHAR(64) NULL DEFAULT NULL,
	`department` VARCHAR(64) NULL DEFAULT NULL,
	`created` DATE NULL DEFAULT NULL,
	PRIMARY KEY (`uid`)
);

CREATE TABLE `userdetail` (
	`uid` INT(10) NOT NULL DEFAULT '0',
	`intro` TEXT NULL,
	`profile` TEXT NULL,
	PRIMARY KEY (`uid`)
)

 */



func main() {


	//打开mysql
	db, err := sql.Open("mysql", "root:dlj@/test")
	checkErr(err)


	/////////////////////////// 1.插入数据 ///////////////////////////////////////

	//准备要执行的sql操作
	//stmt, err := db.Prepare(`INSERT userinfo SET username=?, department=?, created=NOW()`)
	stmt, err := db.Prepare(`INSERT INTO userinfo(username, department, created) values(?,?, NOW())`)
	checkErr(err)

	res, err := stmt.Exec("yqq1", "研发1")
	res, err = stmt.Exec("yqq2", "研发2")
	res, err = stmt.Exec("yqq3", "研发1")
	res, err = stmt.Exec("yqq4", "研发2")
	checkErr(err)

	idLastInsert, _ := res.LastInsertId()   //获取最后一个插入的id号, id是主键
	fmt.Println("idLastInsert:", idLastInsert)
	//////////////////////////////////////////////////////////////////////////////

	/////////////////////////////2.更新数据 ////////////////////////////////////////
	stmt , err = db.Prepare("UPDATE  userinfo set username=? where uid=?;")
	checkErr(err)

	res, err = stmt.Exec("yqq9", 9 )  //返回的affect是 sql语句是影响的 行数
	affect, err := res.RowsAffected()
	checkErr(err)
	fmt.Println(affect)

	////////////////////////////////////////////////////////////////////////////


	//////////////////////////3.查询数据 ////////////////////////////////
	rows, err := db.Query("SELECT  * FROM	userinfo;")
	checkErr(err)

	for rows.Next(){
		var uid, username, department, created  string
		err = rows.Scan(&uid, &username, &department, &created)
		checkErr(err)

		fmt.Println(uid, username, department, created)

	}

	////////////////////////////////////////////////////////////////////



	/////////////////////////////4.删除数据 ////////////////////////////
	stmt, err = db.Prepare("delete from userinfo where uid=?;")
	res, err = stmt.Exec(idLastInsert) // 删除最后条数据

	//res, err = stmt.Exec(1+idLastInsert) // 删除最后条数据
	checkErr(err)

	affectRowsNum, err  := res.RowsAffected()
	checkErr(err)

	fmt.Println("affectRows: ", affectRowsNum)
	db.Close()

	///////////////////////////////////////////////////////////////////////






}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}