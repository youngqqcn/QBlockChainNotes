package list

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestDList(t *testing.T) {
	dlist := NewDList()
	require.Nil(t, dlist.head)
	require.Nil(t, dlist.tail)
	require.Equal(t, dlist.Size(), 0)

	dlist.PushBack(11)
	dlist.PushBack(22)
	dlist.PushBack(33)
	dlist.Print()

	// t.Equal(t, dlist.Size(), 3)
	require.Equal(t, dlist.Size(), 3, "size is error")

	require.Nil(t, dlist.Find(0), "find error" )
	require.NotNil(t, dlist.Find(11), "find error" )
	require.NotNil(t, dlist.Find(22), "find error" )
	require.NotNil(t, dlist.Find(33), "find error" )

	dlist.Delete(11)
	require.Equal(t, dlist.Size(), 2, "size is error")
	require.Nil(t, dlist.Find(11), "find error" )
	dlist.Print()
	require.Equal(t, dlist.head, dlist.Find(22))
	require.Equal(t, dlist.head, dlist.Find(33).Next)
	require.Equal(t, dlist.head.Pre, dlist.Find(33))

	dlist.Delete(33)
	require.Equal(t, dlist.Size(), 1, "size is error")
	require.Nil(t, dlist.Find(33), "find error" )
	dlist.Print()	
	require.Equal(t, dlist.head, dlist.Find(22))
	require.Equal(t, dlist.head, dlist.tail)

	dlist.Delete(22)
	require.Equal(t, dlist.Size(), 0, "size is error")
	require.Nil(t, dlist.Find(22), "find error" )
	dlist.Print()	
	require.Nil(t, dlist.head)
	require.Nil(t, dlist.tail)
	require.Equal(t, dlist.head, dlist.tail)

	require.False(t, dlist.Delete(66))
	for i := 0; i < 10000; i++ {
		dlist.PushBack(ValueType(i))
	}
	for i := 0; i < 10000; i++{
		dlist.Delete(ValueType(i))
	}
	require.Equal(t, dlist.Size(), 0, "size is error")
	require.Nil(t, dlist.head)
	require.Nil(t, dlist.tail)
	require.Equal(t, dlist.head, dlist.tail)

	dlist.PushBack(ValueType("hello"))
	dlist.PushBack(ValueType("goood"))
	dlist.PushBack(ValueType("check"))
	dlist.PushBack(ValueType("out"))
	require.Equal(t, dlist.Size(), 4, "size is error")	
	dlist.Print()
	require.NotNil(t, dlist.Find("out"))
}
