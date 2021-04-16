package container_list_test

import (
	"container/list"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestList(t *testing.T) {

	l := list.New()
	for i := 0; i < 10000; i++ {
		l.PushBack(i)
	}

	cur := l.Front()
	for cur != nil {
		l.Remove(cur)
		cur = l.Front()
	}
	require.Equal(t, l.Len(), 0)
}
