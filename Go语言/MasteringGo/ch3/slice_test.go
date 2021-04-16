package ch3

import (
	"fmt"
	"testing"
)

func TestSlice(t *testing.T) {
	// 1. 切片的定义和初始化操作
	s1 := []int{1, 2, 3, 4}
	s2 := make([]int, 5)
	fmt.Println(s1)
	fmt.Println(s2)
	s2 = nil
	fmt.Println(s2)

	// 2. 使用 [:]以数组创建切片, 切片指向底层数组
	a1 := [4]int{1, 2, 3, 4}
	sa := a1[:]
	fmt.Println(a1)
	fmt.Println(sa)
	a1[0] = 99
	fmt.Println(sa) // 99

	// 3. make 创建byte切片, 二维切片
	bz := make([]byte, 5)
	fmt.Println(bz)
	twos := make([][]int, 5) // 不指定列数, 列是slice, 可以任意多少列
	// twos := make([][10]int, 5) // 指定列数, 列是数组
	fmt.Println(twos)

	// 4. 初始化二维切片
	for row := 0; row < len(twos); row++ {
		for col := 0; col < 10; col++ {
			// twos[row][col] = row * col
			twos[row] = append(twos[row], row*col)
		}
	}
	fmt.Println(twos)

	// 5. 遍历二维数组中的元素
	for row := 0; row < len(twos); row++ {
		for col := 0; col < len(twos[row]); col++ {
			fmt.Printf("%d  ", twos[row][col])
		}
	}
	fmt.Println()

	// 使用range
	for row, sliceRow := range twos {
		for col, item := range sliceRow {
			fmt.Printf("[%d][%d] is %d ", row, col, item)
		}
		fmt.Println()
	}
	fmt.Println()
}
