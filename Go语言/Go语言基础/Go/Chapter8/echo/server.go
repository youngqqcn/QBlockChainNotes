package main

import (
	"flag"
		"net/http"
	"log"
	"html/template"
	"fmt"
	"github.com/gorilla/websocket"
)

/**
*作者: yqq
*日期: 2018/12/3  20:22
*描述: WebSocket
	用  "github.com/gorilla/websocket" 写一个 echo
*/


//处理WebSocket
func echo(w http.ResponseWriter, r *http.Request) {
	var upgrader = websocket.Upgrader{} // use default options
	c, err := upgrader.Upgrade(w, r, nil)  //切换到WebSocket协议
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	defer c.Close()
	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			log.Println("read:", err)
			break
		}
		log.Printf("recv: %s", message)
		err = c.WriteMessage(mt, message)
		if err != nil {
			log.Println("write:", err)
			break
		}
	}
}

//主页面
func home(w http.ResponseWriter, r *http.Request) {
	t, err := template.ParseFiles("./Chapter8/echo/echo.html")
	if err != nil{
		fmt.Println(err)
		return
	}
	t.Execute(w, "ws://"+r.Host+"/echo")
}

func main() {
	flag.Parse()
	log.SetFlags(0)
	http.HandleFunc("/echo", echo)
	http.HandleFunc("/", home)
	var addr = flag.String("addr", "localhost:9999", "http service address")
	log.Fatal(http.ListenAndServe(*addr, nil))
}


