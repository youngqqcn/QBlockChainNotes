package ch3

import (
	"fmt"
	"regexp"
	"testing"
)

func TestRegex(t *testing.T) {
	rexp, err := regexp.Compile(`[\d]{10}`)
	if err != nil {
		fmt.Println(err)
		return
	}

	result := rexp.FindAll([]byte("14kjk0123456789xx0987654321"), -1)
	for _, str := range result {
		fmt.Println(string(str))
	}
}
