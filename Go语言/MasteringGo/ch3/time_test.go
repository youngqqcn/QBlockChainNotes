package ch3

import (
	"context"
	"fmt"
	"testing"
	"time"
)

func TestTime(tst *testing.T) {
	t := time.Now().Format(time.RFC3339)
	fmt.Println(t)
	timer := time.NewTicker(time.Second * 2)

	ctx, cancel := context.WithCancel(context.Background())

	go func() {
		select {
		case <-time.After(time.Second * 10):
			cancel()
		}
	}()

	F := func() error {
		for {
			select {
			case <-timer.C:
				func() {
					fmt.Println("tm triggered")
				}()
			case <-ctx.Done():
				fmt.Println("Done")
				// fmt.Println(ctx.Err())
				return ctx.Err()
			}
		}
	}

	if err := F(); err != nil {
		fmt.Println(err)
	}

}
