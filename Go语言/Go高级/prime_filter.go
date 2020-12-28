package main

import (
	"fmt"
	"net/http"
	_ "net/http/pprof"
	"runtime"
)

func genPrimeNumber() (ch chan int) {
	ch = make(chan int, 1)
	go func() {
		for i := 2; ; i++ {
			ch <- i
			// fmt.Printf("[gen %v ] ", i)
		}
	}()
	return
}

func primeNumberFilter(ch <-chan int, p int) (out chan int) {
	// fmt.Printf("创建筛子:[%v], [%v]\n", ch, p)
	out = make(chan int, 1)
	go func() {
		for {
			n := <-ch
			// fmt.Printf("[ch=%v, n=%v , p=%v ]", ch, n, p)
			if (n % p) != 0 {
				out <- n
			}
		}
	}()
	return
}

func main() {

	runtime.GOMAXPROCS(0)

	ch := genPrimeNumber()
	fmt.Printf("&ch = %v\n\n\n", &ch)
	fmt.Println()

	for i := 0; i < 100; i++ {
		n := <-ch
		fmt.Printf("  ====> %v ", n)

		// 新的channel, 给ch赋值, 不会影响之前的已经生成的channel, 所以,之前的那些筛子仍然可以向老的channel中发送数据
		ch = primeNumberFilter(ch, n)
		fmt.Printf("new channel = %v\n", ch)
	}

	fmt.Printf("=======================\n")
	ip := "0.0.0.0:9001"
	if err := http.ListenAndServe(ip, nil); err != nil {
		fmt.Printf("start pprof failed on %s\n", ip)
	}

}
