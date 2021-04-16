package ch3

import (
	"fmt"
	"testing"
)

func TestMap(t *testing.T) {
	m1 := make(map[string]string)
	m1["name"] = "test"
	m1["tag"] = "send"
	m1["amount"] = "add"

	for key, value := range m1 {
		fmt.Printf("%s: %s\n", key, value)
	}

	fmt.Println(m1)

	delete(m1, "tag")
	fmt.Println(m1)

	m1 = nil
	fmt.Println(m1)
	m1["good"] = "ok"
	fmt.Println(m1)
}
