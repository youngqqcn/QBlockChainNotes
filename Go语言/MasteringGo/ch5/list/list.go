package list

import "fmt"

type ValueType interface {}

type node struct {
	Pre   *node
	Next  *node
	Value ValueType
}

func newNode(Value ValueType) *node {
	return &node{
		Value: Value,
	}
}

type DList struct {
	head *node
	tail *node
	size int
}

func NewDList() *DList {
	return &DList{head: nil, tail: nil, size: 0}
}

func (d *DList) PushBack(value ValueType)  {
	nd := newNode(value)
	// empty
	if d.size == 0 {
		d.head = nd
		d.tail = nd
		nd.Pre = nd
		nd.Next = nd
		d.size += 1
	} else {
		// not empty
		d.tail.Next = nd
		nd.Pre = d.tail
		nd.Next = d.head
		d.tail = nd
		d.head.Pre = d.tail
		d.size += 1
	}
}

func (d *DList) Delete(value ValueType) bool {
	n := d.Find(value)
	if n != nil {
		if d.size == 1 {
			d.head = nil
			d.tail = nil
		}

		n.Pre.Next = n.Next
		n.Next.Pre = n.Pre

		if n == d.head {
			d.head = n.Next
			d.tail.Next = d.head
		}
		if n == d.tail {
			d.tail = n.Pre
			d.head.Pre = d.tail
		}
		d.size -= 1
	}
	return false
}

func (d DList) Find(value ValueType) *node {
	search := d.head
	for i := 0; i < d.size; i++ {
		if search.Value == value {
			return search
		}
		search = search.Next
	}
	return nil
}

func (d DList) Size() int {
	return d.size
}

func (d DList) Print() {
	cur := d.head
	for i := 0; i < d.Size(); i++ {
		fmt.Printf("%v  ", cur.Value)
		cur = cur.Next
	}
	fmt.Printf("\n")
}
