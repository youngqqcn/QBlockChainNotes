package ch8

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"testing"
)

func TestWalk(t *testing.T) {

	walk := func(path string, info fs.FileInfo, err error) error {
		finfo, err := os.Stat(path)
		if err != nil {
		}

		mode := finfo.Mode()
		if mode.IsRegular() {
			fmt.Println("r", path)
			return nil
		}

		if mode.IsDir() {
			fmt.Println("d", path)
			return nil
		}

		// what's this?
		fmt.Println(path)
		return nil
	}

	err := filepath.Walk("../", walk)
	if err != nil {
		fmt.Println(err)
	}

}
