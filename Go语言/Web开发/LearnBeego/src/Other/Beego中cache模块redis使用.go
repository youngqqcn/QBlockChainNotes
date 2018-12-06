package main

import (
	_ "github.com/astaxie/beego/cache/redis"
	"github.com/astaxie/beego/cache"
	"time"
	"fmt"
	"github.com/gomodule/redigo/redis"
)

func TestRedisCache( ) {
	bm, err := cache.NewCache("redis", `{"conn": "127.0.0.1:6379"}`)
	if err != nil{
		fmt.Println("连接redis失败")
		return
	}

	bm.Put("stuName", "yqq", time.Second * 100)

	stuName , err := redis.String( bm.Get("stuName"), err )
	if err != nil{
		fmt.Println(err)
		return
	}
	fmt.Println(stuName)


	err = bm.Delete("stuName")
	if err != nil{
		fmt.Println("delete err")
		return
	}





}

func main()  {

	TestRedisCache()

}

