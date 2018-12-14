package main

import (
	"github.com/boltdb/bolt"
	"fmt"
	"log"
)

/**
*作者: yqq
*日期: 2018/12/14  11:52
*描述: 练习使用boltDB
*/

func main() {


	db, err := bolt.Open("mytest.db", 0600, nil)
	if err != nil{
		log.Panic(err)
	}
	defer db.Close()

	//读写数据库
	err = db.Update(func(tx *bolt.Tx) error {

		/*
		bucket := tx.Bucket([]byte("MyBucket"))

		//如果数据库已经存在
		if bucket != nil{
			return nil
		}

		//创建bucket
		bucket, err := tx.CreateBucket([]byte("MyBucket"))
		if err != nil{
			log.Panic(err)
		}
		*/


		bucket , err := tx.CreateBucketIfNotExists([]byte("MyBucket"))
		if err != nil{
			fmt.Println("创建数据库失败:", err)
			return  nil
		}

		//将key/value写入Bucket
		err = bucket.Put([]byte("name"), []byte("yqq"))
		if err != nil{
			log.Panic(err)
		}
		err = bucket.Put([]byte("name"), []byte("这是名字")) //如果name字段之前存在, 则会更新name的值
		if err != nil{
			log.Panic(err)
		}
		fmt.Println("写入成功")
		return nil
	})


	db.View(func(tx *bolt.Tx) error {
		bucket := tx.Bucket([]byte("MyBucket"))
		if bucket == nil{
			fmt.Println("没有MyBucket数据库")
			return nil
		}
		value := string(bucket.Get([]byte("name")))


		fmt.Println(value)
		return  nil
	})


	db.Update(func(tx *bolt.Tx) error {
		/*
		bucket := tx.Bucket([]byte("MyBucket")) //获取数据库
		if bucket == nil{ //如果数据库不存在
			return nil
		}

		err := bucket.Delete([]byte("name")) //删除字段
		if err != nil{
			fmt.Println(err)
			return nil
		}
		fmt.Println("删除字段成功")
		*/


		bucket := tx.Bucket([]byte("MyBucket")) //获取数据库
		bucket.CreateBucket([]byte("Bucket2"))
		err = bucket.DeleteBucket([]byte("Bucket2")) //删除目标数据库
		if err != nil{
			fmt.Println("删除数据库失败", err)
			return nil
		}
		fmt.Println("删除数据库成功")

		//err := bucket.DeleteBucket([]byte("MyBucket")) //删除目标数据库

		err = tx.DeleteBucket([]byte("MyBucket"))
		if err != nil{
			fmt.Println(err)
		}
		return nil
	})

	if err != nil{
		log.Panic(err)
	}

}
