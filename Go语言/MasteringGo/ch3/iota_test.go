package ch3

import (
	"fmt"
	"testing"
)

const (
	One int = iota + 1
	Two
	Three
	Six int = iota + 3
	Seven
)

func TestIota(t *testing.T) {
	fmt.Println(One)
	fmt.Println(Seven)
}
