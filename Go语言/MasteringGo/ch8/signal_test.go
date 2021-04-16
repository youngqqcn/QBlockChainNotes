package ch8

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"testing"
	"time"
)

func TestSignal(t *testing.T) {
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGINT)

	go func() {

		for {
			sig := <-sigCh
			switch sig {
			// SIGKILL SIGSTOP 不能被捕获
			case syscall.SIGINT:
				fmt.Println("signal: ", sig)
			case os.Interrupt:
				fmt.Println("interrupt: ", sig)
				return
			}
		}

	}()

	select {
	case <-time.After(time.Second * 3):
		fmt.Println("end")
	}
}
