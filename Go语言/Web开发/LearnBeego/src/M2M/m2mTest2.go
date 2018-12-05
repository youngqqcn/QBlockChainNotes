package main



/**
*作者: yqq
*日期: 2018/12/5  23:40
*描述: n
*/
import (
	_ "github.com/go-sql-driver/mysql"
	"github.com/astaxie/beego/orm"
	"time"
	"log"
)


type MainFields struct {
	Id int `orm:"auto"`
	Created time.Time `orm:"auto_now_add;type(datetime)"`
	Updated time.Time `orm:"auto_now;type(datetime)"`
}

type Game struct {
	MainFields
	Players  []*Player `orm:"rel(m2m)"`
}

type Player struct {
	MainFields
	Games []*Game `orm:"revers	e(many)"`
	NickName string
}


func init() {
	// 需要在init中注册定义的model
	orm.RegisterDataBase("default", "mysql", "root:dlj@/test1", 30)
	orm.RegisterModel(new(Game), new(Player))
	// 需要在init中注册定义的model
	orm.RunSyncdb("default", false, true)
}

func insertTestData() {

	o := orm.NewOrm()

	var playerA Player
	playerA.NickName = "CoolDude"
	id, err := o.Insert(&playerA)
	if err != nil {
		log.Printf(err.Error())
	} else {
		log.Printf("Player ID: %v", id)
	}

	var game Game
	id, err = o.Insert(&game)
	if err != nil {
		log.Printf(err.Error())
	} else {
		log.Printf("Game ID: %v", id)
	}

	m2m := o.QueryM2M(&game, "Players")
	num, err := m2m.Add(playerA)
	if err == nil {
		log.Printf("Added nums: %v", num)
	}
}


//测试 多对多 ok
func insertTestData2() {

	o := orm.NewOrm()

	var playerA Player
	playerA.NickName = "CoolDude"
	o.Insert(&playerA)

	var playerB Player
	playerB.NickName = "yqq"
	o.Insert(&playerB)

	var game Game
	o.Insert(&game)
	var game2 Game
	o.Insert(&game2)

	m2m := o.QueryM2M(&game, "Players")
	m2m.Add(playerA)
	m2m.Add(playerB)

	m2m2 := o.QueryM2M(&game2, "Players")
	m2m2.Add(playerB)

/*

game表
+----+---------------------+---------------------+
| id | created             | updated             |
+----+---------------------+---------------------+
|  1 | 2018-12-05 15:55:39 | 2018-12-05 15:55:39 |
|  2 | 2018-12-05 15:55:39 | 2018-12-05 15:55:39 |
+----+---------------------+---------------------+

game_players表
+----+---------+-----------+
| id | game_id | player_id |
+----+---------+-----------+
|  1 |       1 |         1 |
|  2 |       1 |         2 |
|  3 |       2 |         2 |
+----+---------+-----------+

player表
+----+---------------------+---------------------+-----------+
| id | created             | updated             | nick_name |
+----+---------------------+---------------------+-----------+
|  1 | 2018-12-05 15:55:39 | 2018-12-05 15:55:39 | CoolDude  |
|  2 | 2018-12-05 15:55:39 | 2018-12-05 15:55:39 | yqq       |
+----+---------------------+---------------------+-----------+

 */

}


//多对多 查询
func querym2m()  {

	//改日完成

}




func main() {
	insertTestData2()

}
