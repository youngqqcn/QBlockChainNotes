package main

import (
	"errors"
	"fmt"
)


//编译执行下面代码会出现什么?

var ErrDidNotWork = errors.New("did not work")

func DoTheThing(reallyDoIt bool) (err error) {
	if reallyDoIt {
		result, err := tryTheThing()
		if err != nil || result != "it worked" {
			err = ErrDidNotWork
		}
	}
	return err
}

func tryTheThing() (string,error)  {
	return "",ErrDidNotWork
}

func main() {
	fmt.Println(DoTheThing(true))
	fmt.Println(DoTheThing(false))
}

