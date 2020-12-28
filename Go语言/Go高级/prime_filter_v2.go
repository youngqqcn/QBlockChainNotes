package main

import (
	"context"
	"fmt"
	"net/http"
	_ "net/http/pprof"
	"runtime"
	"time"
)

func genPrimeNumber(ctx context.Context) (out chan int) {
	out = make(chan int)
	go func() {
		// defer fmt.Printf("genPrimeNumber goroutine finised\n")
		for i := 2; ; i++ {
			select {
			case out <- i:
			case <-ctx.Done(): // finish this goroutine
				return
			}
		}

	}()
	return
}

func primeNumberFilter(ctx context.Context, in <-chan int, prime int) (out chan int) {
	out = make(chan int)
	go func() {
		for {
			select {
			case n := <-in:
				if (n % prime) != 0 {
					select {
					case out <- n:
						break
					case <-ctx.Done():
						return
					}
				}
			case <-ctx.Done():
				return

			// 取消default会大大提高效率!
			// default:
				// continue
			}
		}
	}()
	return
}

func primeNumberFilter(ctx context.Context, in <-chan int, prime int) (out chan int) {
	out = make(chan int)
	go func() {
		for {
			if n := <-in; (n % prime) != 0 { // 会导致很多goroutine阻塞在 n := <-in 无法退出
				select {
				case out <- n:
					break
				case <-ctx.Done():
					return
				}
			}
		}
	}()
	return
}

func main() {

	defer func() {
		time.Sleep(1 * time.Second)
		fmt.Println("the number of goroutines: ", runtime.NumGoroutine())
	}()
	fmt.Println("the number of goroutines: ", runtime.NumGoroutine()) // 1
	ctx, cancel := context.WithCancel(context.Background())

	ch := genPrimeNumber(ctx)

	fmt.Println("the number of goroutines: ", runtime.NumGoroutine()) // 2
	for i := 0; i < 100; i++ {
		n := <-ch
		fmt.Printf("%d -> %d\n", i, n)
		ch = primeNumberFilter(ctx, ch, n)
	}
	cancel()

	time.Sleep(1 * time.Second)
	fmt.Println("the number of goroutines: ", runtime.NumGoroutine())
	// time.Sleep(5 * time.Second)

	ip := "0.0.0.0:9001"
	if err := http.ListenAndServe(ip, nil); err != nil {
		fmt.Printf("start pprof failed on %s\n", ip)
	}
}
