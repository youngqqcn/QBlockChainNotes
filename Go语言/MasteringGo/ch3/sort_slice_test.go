package ch3

import (
	"fmt"
	"sort"
	"testing"
)

type Box struct {
	name    string
	num     int
	balance float64
}

func (b Box) String() string {
	return fmt.Sprintf("{name=%s, num=%d, balance=%f}", b.name, b.num, b.balance)
}

type Boxs struct {
	boxs []Box
}

//======== 实现 sort interface
func (b Boxs) Len() int {
	return len(b.boxs)
}

func (b Boxs) Less(i, j int) bool {
	return b.boxs[i].balance < b.boxs[j].balance
}

func (b *Boxs) Swap(i, j int) {
	b.boxs[i], b.boxs[j] = b.boxs[j], b.boxs[i]
}

func (b *Boxs) String() string {
	var ret string
	for idx, box := range b.boxs {
		ret += fmt.Sprintf("%d==>%s\n", idx, box.String())
	}
	return ret
}

//=======================

func TestSort(t *testing.T) {

	// 1.对普通slice排序
	s1 := []int{10, -2, 43, 24, 20, 15}
	sort.Slice(s1, func(i, j int) bool {
		return s1[i] < s1[j]
	})
	println(s1)
	fmt.Println(s1)

	// 2.对结构体slice排序
	s2 := []Box{
		{
			name:    "htdf",
			num:     50,
			balance: 5.8234,
		},
		{
			name:    "eth",
			num:     200,
			balance: 1.8234,
		},
		{
			name:    "btc",
			num:     30,
			balance: 2.89234,
		},
		{
			name:    "rtc",
			num:     34,
			balance: 7.89234,
		},
	}

	bxs := Boxs{boxs: s2}
	sort.Sort(&bxs)
	fmt.Println(bxs)
	fmt.Println("===================================")

	sort.Slice(s2, func(i, j int) bool {
		return s2[i].balance < s2[j].balance
	})
	fmt.Println(s2)
}
