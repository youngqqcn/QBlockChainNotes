package heap

import "container/heap"

// 实现以下接口, 即可实现 堆
// type Interface interface {
// 	sort.Interface
// 	Push(x interface{}) // add x as element Len()
// 	Pop() interface{}   // remove and return element Len() - 1.
// }

type MyHeap []int

func NewMyHeap() *MyHeap {
	h := MyHeap{}
	heap.Init(&h)
	return &h
}

// func (h *MyHeap) Add(x interface{}) {
// 	heap.Push(h, x)
// }

// func (h *MyHeap) Get() interface{} {
// 	return heap.Pop(h)
// }

// 实现 container/heap
func (h *MyHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *MyHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// Len is the number of elements in the collection.
func (h MyHeap) Len() int {
	return len(h)
}

// 小根堆
func (h MyHeap) Less(i, j int) bool {
	return h[i] < h[j]
}

func (h *MyHeap) Swap(i, j int) {
	(*h)[i], (*h)[j] = (*h)[j], (*h)[i]
}
