package main

/**
*作者: yqq
*日期: 2018/12/2  22:24
*描述:


如果   ExampleNewClient()  测试结果不是  "PONG<nil>" , 提示 被拒绝
可能是 redis 设置保护模式

修改  /etc/redis/redis.conf 文件,  如下

1>注释掉bind
#bind 127.0.0.1
2>默认不是守护进程方式运行，这里可以修改
daemonize no                  //window不支持守护进程
3>禁用保护模式
protected-mode no

然后重启   sudo  /etc/init.d/redis-server restart   重启redis-server  , 再次连接测试



如果是 Window 平台下的 redis ,  修改安装目录下的  redis.window.conf ,
修改方法同linux 然后重启redis-server即可


*/

import (
	"github.com/go-redis/redis"
	"fmt"
)



func ExampleNewClient() {
	client := redis.NewClient(&redis.Options{
		Addr:     "192.168.150.138:6379", //ubuntu
		//Addr:     ":6379", //本机 127.0.0.1:6379
		Password: "", // no password set
		DB:       0,  // use default DB
	})

	pong, err := client.Ping().Result()
	fmt.Println(pong, err)
	// Output: PONG <nil>
}

//
//func main() {
//
//		ExampleNewClient()
//}
func main() {
	fmt.Println("This is a program for go to use go_redis.")

	//connect
	cl := redis.NewClient(&redis.Options{
		//Addr:     "192.168.150.138:6379", //我的ubuntu
		Addr: ":6379",
	})
	cl.WrapProcess(func(old func(cmd redis.Cmder) error) func(cmd redis.Cmder) error {
		return func(cmd redis.Cmder) error {
			fmt.Printf("starting process:<%s>\n", cmd)
			err := old(cmd)
			fmt.Printf("finished process:<%s>\n", cmd)
			return err
		}
	})

	//get
	Get := func(client *redis.Client, key string) *redis.StringCmd {
		cmd := redis.NewStringCmd("get", key)
		client.Process(cmd)
		return cmd
	}

	//set
	Set := func(client *redis.Client, key string, value string) *redis.StringCmd {
		cmd := redis.NewStringCmd("set", key, value)
		client.Process(cmd)
		return cmd
	}

	//use
	_, errSet := Set(cl, "myKey", "myValue").Result()
	if errSet != nil {
		fmt.Println("redis set failed.", errSet)
	}
	value, errGet := Get(cl, "myKey").Result()
	if errGet != nil {
		fmt.Println("redis get failed.", errGet)
	} else {
		fmt.Println("The key value is", value)
	}

	//something else
	cmd := redis.NewStringCmd("set", "myKey1", "123", "ex", "100")
	cl.Process(cmd)

	//get expire
	cmd1 := redis.NewIntCmd("ttl", "myKey1")
	cl.Process(cmd1)
	expire, errEx := cmd1.Result()
	if errEx != nil {
		fmt.Println("ttl failed.", errEx)
	} else {
		fmt.Println("expire of key is", expire)
	}

}


