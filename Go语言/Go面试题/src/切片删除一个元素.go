package main

import (
	"errors"
	"fmt"
)

type Slice []int


func (s*Slice)Remove(value interface{}) error {
	for i, v:= range *s {
		if value == v  {
			*s =append((*s)[:i],(*s)[i + 1:]...)
			return nil
		}
	}

	return errors.New("未找到")
}


func  main()  {
	s := make([]int, 0)
	//s := make([]int, 3)
	s = append(s, 1, 2, 3, 4)
	fmt.Println(s)

	slice := Slice{}
	slice = s
	fmt.Println(slice[4])
	slice.Remove(4)

	fmt.Println(slice)

}






