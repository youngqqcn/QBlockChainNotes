package main

import (
	"github.com/bradfitz/gomemcache/memcache"
	"fmt"
	"log"
)






func  main()  {

	mc := memcache.New("127.0.0.1:11211")
	if mc == nil{
		fmt.Println("New failed:")
		return
	}

	//set操作
	//set key flags exptime bytes [noreply]
	//value
	//例如:
	//set runoob 0 900 9
	//memcached
	item := memcache.Item{Key:"myName", Value:[]byte("你好") }
	err := mc.Set(&item)
	if err != nil{
		log.Println(err)
		return
	}

	//get操作
	//get key1 key2 key3
	it , err := mc.Get("myName")
	if err != nil{
		log.Println(err)
		return
	}
	fmt.Println("value ==>", string(it.Value))


	//add操作
	//add key flags exptime bytes [noreply]
	//value
	//例如:
	//add new_key 0 900 10
	//data_value
	err = mc.Add(&memcache.Item{Key:"age", Value:[]byte("1")})
	if err != nil{
		log.Println(err)
		//return
	}
	//get操作
	it , err = mc.Get("age")
	if err != nil{
		log.Println(err)
		return
	}
	fmt.Println("value ==>", string(it.Value))


	//replace操作
	//replace key flags exptime bytes [noreply]
	//value
	//例如:
	//replace mykey 0 900 16
	//some_other_value
	mc.Replace(&memcache.Item{Key:"myName" , Value:[]byte("hello")})
	//get操作
	it , err = mc.Get("myName")
	if err != nil{
		log.Println(err)
		return
	}
	fmt.Println("value ==>", string(it.Value))


	//delete操作
	//delete key [noreply]
	//例如:
	//delete runoob
	err = mc.Delete("myName")
	if err != nil{
		fmt.Println(err)
		return
	}


	//mc.Increment()
	//mc.Decrement()

	//mc.FlushAll()

	//mc.GetMulti()


}
