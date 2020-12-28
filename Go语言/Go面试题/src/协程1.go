package main

import (
	"fmt"
	"runtime"

	// "runtime"
	"sync"
)

//运行结果是?

// func main() {
// 	runtime.GOMAXPROCS(1)
// 	wg := sync.WaitGroup{}
// 	wg.Add(20)
// 	for i := 0; i < 10; i++ {
// 		go func() {
// 			fmt.Println("A: ", i)
// 			wg.Done()
// 		}()
// 		// time.Sleep(time.Duration(0)*time.Second)
// 		runtime.Gosched()
// 	}
// 	for i := 0; i < 10; i++ {
// 		go func(i int) {
// 			fmt.Println("B: ", i)
// 			wg.Done()
// 		}(i)
// 	}
// 	fmt.Println("hello")
// 	wg.Wait()
// }

// func main() {
// 	runtime.GOMAXPROCS(1) //设置同一时间只能运行一个协程
// 	wg := sync.WaitGroup{}
// 	wg.Add(20)
// 	for i := 0; i < 10; i++ {
// 		go func() {
// 			fmt.Println("A: ", i, ", &i=", &i)
// 			wg.Done()
// 		}()
// 		time.Sleep(1000)
// 	}
// 	for i := 0; i < 10; i++ {
// 		go func(i int) {
// 			fmt.Println("B: ", i, ", &i=", &i)
// 			wg.Done()
// 		}(i)
// 	}
// 	wg.Wait()
// }

// func main() {
// 	runtime.GOMAXPROCS(0) //设置同一时间只能运行一个协程
// 	wg := sync.WaitGroup{}

// 	goRoutineCount := runtime.NumCPU()
// 	wg.Add(goRoutineCount)

// 	var loopNum uint64 = 100000000
// 	var x uint64 = 0
// 	for i := 0; i < goRoutineCount; i++ {
// 		go func() {
// 			for n := uint64(0); n < loopNum; n++ {
// 				x += 1
// 			}
// 			wg.Done()
// 		}()
// 	}
// 	wg.Wait()

// 	expectedNumber := uint64(goRoutineCount) * uint64(loopNum)
// 	if x != expectedNumber {
// 		fmt.Printf("错误\n")
// 	}else {
// 		fmt.Printf("正确\n")
// 	}
// }

// func main() {
// 	runtime.GOMAXPROCS(0) //设置同一时间只能运行一个协程
// 	wg := sync.WaitGroup{}

// 	goRoutineCount := runtime.NumCPU()
// 	wg.Add(goRoutineCount)

// 	var loopNum uint64 = 100000
// 	var x uint64 = 0
// 	for i := 0; i < goRoutineCount; i++ {
// 		go func() {
// 			for n := uint64(0); n < loopNum; n++ {
// 				atomic.AddUint64(&x, 1)
// 			}
// 			wg.Done()
// 		}()
// 	}

// 	wg.Wait()

// 	expectedNumber := uint64(goRoutineCount) * uint64(loopNum)
// 	if x != expectedNumber {
// 		fmt.Printf("错误\n")
// 	} else {
// 		fmt.Printf("正确\n")
// 	}
// }

// func main() {

// 	var a int = 10
// 	wg := sync.WaitGroup{}
// 	wg.Add(1)
// 	go func() {
// 		fmt.Printf("&a = %v\n", &a)
// 		wg.Done()
// 	}()

// 	fmt.Printf("&a = %v\n", &a)
// 	wg.Wait()
// }

// type MyCounter struct {
// 	sync.Mutex
// 	x uint64
// }

// func NewMyCounter(n uint64) *MyCounter {
// 	return &MyCounter{
// 		x: n,
// 	}
// }

// func (cnt *MyCounter) Add(n uint64) {
// 	cnt.Lock()
// 	defer cnt.Unlock()
// 	cnt.x += 1
// }

// func (cnt *MyCounter) Get() uint64 {
// 	return cnt.x
// }

// func main() {
// 	runtime.GOMAXPROCS(0) // CPU数
// 	wg := sync.WaitGroup{}

// 	goRoutineCount := runtime.NumCPU()
// 	wg.Add(goRoutineCount)

// 	var loopNum uint64 = 100000
// 	// var x uint64 = 0

// 	x := NewMyCounter(0)
// 	for i := 0; i < goRoutineCount; i++ {
// 		go func() {
// 			for n := uint64(0); n < loopNum; n++ {
// 				// atomic.AddUint64(&x, 1)
// 				x.Add(1)
// 			}
// 			wg.Done()
// 		}()
// 	}

// 	wg.Wait()

// 	expectedNumber := uint64(goRoutineCount) * uint64(loopNum)
// 	if x.Get() != expectedNumber {
// 		fmt.Printf("错误\n")
// 	} else {
// 		fmt.Printf("正确\n")
// 	}
// }

// func main() {
// 	runtime.GOMAXPROCS(0) // CPU数
// 	wg := sync.WaitGroup{}

// 	goRoutineCount := runtime.NumCPU()
// 	wg.Add(goRoutineCount)

// 	var loopNum uint64 = 100000
// 	var x uint64 = 0

// 	// 思考: 如果改称 make(chan bool) 或 make(chan bool, 0)是否可以? make(chan bool, 10000)呢?
// 	ch := make(chan bool, 1)
// 	ch <- true
// 	for i := 0; i < goRoutineCount; i++ {
// 		go func() {
// 			for n := uint64(0); n < loopNum; n++ {
// 				<-ch
// 				x += 1
// 				ch <- true
// 			}
// 			wg.Done()
// 		}()
// 	}

// 	wg.Wait()

// 	expectedNumber := uint64(goRoutineCount) * uint64(loopNum)
// 	if x != expectedNumber {
// 		fmt.Printf("错误\n")
// 	} else {
// 		fmt.Printf("正确\n")
// 	}
// }

func main() {
	runtime.GOMAXPROCS(0) // CPU数
	wg := sync.WaitGroup{}

	goRoutineCount := runtime.NumCPU()
	wg.Add(goRoutineCount)

	var loopNum uint64 = 100000
	var x uint64 = 0

	var flag bool = false
	for i := 0; i < goRoutineCount; i++ {
		go func() {
			for n := uint64(0); n < loopNum; n++ {
				for !flag {
				} // 等待flag
				flag = false 
				x += 1
				flag = true
			}
			wg.Done()
		}()
	}
	flag = true

	wg.Wait()

	expectedNumber := uint64(goRoutineCount) * uint64(loopNum)
	if x != expectedNumber {
		fmt.Printf("错误\n")
	} else {
		fmt.Printf("正确\n")
	}
}
