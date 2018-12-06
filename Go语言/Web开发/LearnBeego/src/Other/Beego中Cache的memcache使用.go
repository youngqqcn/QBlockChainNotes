package main

import (
	_ "github.com/astaxie/beego/cache/memcache"
	"github.com/astaxie/beego/cache"
	"time"
	"strconv"
	"fmt"
)

// Copyright 2014 beego Author. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


func TestMemcacheCache() {
	bm, err := cache.NewCache("memcache", `{"conn": "127.0.0.1:11211"}`)
	if err != nil {
		fmt.Println("init err")
	}
	timeoutDuration := 10 * time.Second
	if err = bm.Put("astaxie", "1", timeoutDuration); err != nil {
		fmt.Println("set Error", err)
	}
	if !bm.IsExist("astaxie") {
		fmt.Println("check err")
	}

	time.Sleep(11 * time.Second)

	if bm.IsExist("astaxie") {
		fmt.Println("check err")
	}
	if err = bm.Put("astaxie", "1", timeoutDuration); err != nil {
		fmt.Println("set Error", err)
	}

	if v, err := strconv.Atoi(string(bm.Get("astaxie").([]byte))); err != nil || v != 1 {
		fmt.Println("get err")
	}

	if err = bm.Incr("astaxie"); err != nil {
		fmt.Println("Incr Error", err)
	}

	if v, err := strconv.Atoi(string(bm.Get("astaxie").([]byte))); err != nil || v != 2 {
		fmt.Println("get err")
	}

	if err = bm.Decr("astaxie"); err != nil {
		fmt.Println("Decr Error", err)
	}

	if v, err := strconv.Atoi(string(bm.Get("astaxie").([]byte))); err != nil || v != 1 {
		fmt.Println("get err")
	}
	bm.Delete("astaxie")
	if bm.IsExist("astaxie") {
		fmt.Println("delete err")
	}

	//test string
	if err = bm.Put("astaxie", "author", timeoutDuration); err != nil {
		fmt.Println("set Error", err)
	}
	if !bm.IsExist("astaxie") {
		fmt.Println("check err")
	}

	if v := bm.Get("astaxie").([]byte); string(v) != "author" {
		fmt.Println("get err")
	}

	//test GetMulti
	if err = bm.Put("astaxie1", "author1", timeoutDuration); err != nil {
		fmt.Println("set Error", err)
	}
	if !bm.IsExist("astaxie1") {
		fmt.Println("check err")
	}

	vv := bm.GetMulti([]string{"astaxie", "astaxie1"})
	if len(vv) != 2 {
		fmt.Println("GetMulti ERROR")
	}
	if string(vv[0].([]byte)) != "author" && string(vv[0].([]byte)) != "author1" {
		fmt.Println("GetMulti ERROR")
	}
	if string(vv[1].([]byte)) != "author1" && string(vv[1].([]byte)) != "author" {
		fmt.Println("GetMulti ERROR")
	}

	// test clear all
	if err = bm.ClearAll(); err != nil {
		fmt.Println("clear all err")
	}
}

func  main()  {
	TestMemcacheCache()
}
