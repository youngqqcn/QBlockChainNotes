package ch4

import (
	"fmt"
	"testing"
)

type Master struct {
	name    string
	area    string
	Balance float64
}

func NewMaster(name string, area string, balance float64) *Master {

	// 这里返回结构体指针, 注意和C/C++ 中返回局部变量地址的区别,
	// Golang会进行"逃逸"分析来决定对象在何处创建
	return &Master{
		name:    name,
		area:    area,
		Balance: balance,
	}
}

func TestStructure(t *testing.T) {

	mst := NewMaster("htdf", "China", 96000000)
	fmt.Println(mst)

	mst2 := new(Master) // 创建了 *Master
	if mst2 == nil {
		fmt.Println("mst2 is nil")
	}
	mst2 = mst // mst2 指向 mst
	fmt.Println(mst2)

	mst2.Balance = 99
	fmt.Println(mst)
	fmt.Println(mst2)
}
