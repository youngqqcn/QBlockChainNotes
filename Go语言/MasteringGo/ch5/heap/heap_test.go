package heap

import (
	"container/heap"
	"testing"
)

func TestMyHeap(t *testing.T) {
	h := NewMyHeap()
	heap.Push(h, 6)
	heap.Push(h, 4)
	heap.Push(h, 2)
	heap.Push(h, 7)
	heap.Push(h, 0)
	heap.Push(h, 5)

	for h.Len() > 0 {
		t.Log(heap.Pop(h))
	}
}
