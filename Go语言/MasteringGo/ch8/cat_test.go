package ch8

import (
	"bufio"
	"io"
	"os"
	"testing"
)

func TestCat(t *testing.T) {

	filename := "test.txt"
	f, err := os.Open(filename)
	if err != nil {
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		io.WriteString(os.Stdout, scanner.Text())
		io.WriteString(os.Stdout, "\n")
	}

}
