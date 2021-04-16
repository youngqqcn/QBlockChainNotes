package ch9

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestGoroutines(t *testing.T) {

	wg := &sync.WaitGroup{}
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(i int) {
			fmt.Println(i)
			time.Sleep(time.Second * 5)
			wg.Done()
		}(i)
	}

	wg.Wait()
	fmt.Println(" all goroutine finished")
}
