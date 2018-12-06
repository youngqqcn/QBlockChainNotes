package main

import (
	"github.com/gomodule/redigo/redis"
	"fmt"
)


func main() {
	c, err := redis.Dial("tcp", "127.0.0.1:6379")
	//c, err := redis.Dial("tcp", "192.168.150.138:6379")
	if err != nil {
		fmt.Println("Connect to redis error", err)
		return
	}
	defer c.Close()

	_, err = c.Do("SET", "mykey", "superWang")
	if err != nil {
		fmt.Println("redis set failed:", err)
	}

	username, err := redis.String(c.Do("GET", "mykey"))
	if err != nil {
		fmt.Println("redis get failed:", err)
	} else {
		fmt.Printf("Get mykey: %v \n", username)
	}
}
