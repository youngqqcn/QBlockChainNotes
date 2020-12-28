package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

func worker(ctx context.Context, wg *sync.WaitGroup) error {
	defer wg.Done()

	for {
		select {
		default:
			// fmt.Println("goooo")
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	fmt.Printf("goooooooooooooooood\n")
	return nil
}

func main() {

	wg := sync.WaitGroup{}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	// defer cancel() // 等超时自动结束

	count := 10
	// wg.Add(count)
	for i := 0; i < count; i++ {
		wg.Add(1)
		go worker(ctx, &wg)
	}
	time.Sleep(time.Second)
	cancel() // 主动结束
	wg.Wait()
}
