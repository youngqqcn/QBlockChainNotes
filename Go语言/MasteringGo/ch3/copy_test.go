package ch3

import (
	"fmt"
	"testing"
)

func TestCopy(t *testing.T) {

	a1 := [5]int{11, 22, 33, 4, 5}
	s1 := []int{1, 2, 3}

	// 拷贝长度取决于两个slice中长度最小的
	copy(s1, a1[:])
	fmt.Println(s1)
}
