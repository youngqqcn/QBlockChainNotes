package ch4

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"testing"
)

type element struct {
	Name    string
	Surname string
	Id      string
}

type KVStore struct {
	db map[string]element
}

func NewKVStore() *KVStore {
	return &KVStore{
		db: make(map[string]element),
	}
}

func (st *KVStore) Add(key string, value element) bool {
	if st.Search(key) == nil {
		st.db[key] = value
		return true
	}
	return false
}

func (st *KVStore) Delete(key string) bool {
	if st.Search(key) != nil {
		delete(st.db, key)
		return true
	}
	return false
}

func (st KVStore) Search(key string) *element {
	if e, ok := st.db[key]; ok {
		return &e
	}
	return nil
}

func (st KVStore) Print() {
	for key, value := range st.db {
		fmt.Printf("%s: %s\n", key, value)
	}
}

func (st *KVStore) Update(key string, value element) bool {
	e := st.Search(key)
	if e == nil {
		return false
	}
	st.db[key] = value
	return true
}

func TestKVStore(t *testing.T) {

	store := NewKVStore()
	scanner := bufio.NewScanner(os.Stdin) // 标准输入
	for scanner.Scan() {
		text := scanner.Text()
		text = strings.TrimSpace(text)
		tokens := strings.Fields(text)

		if len(tokens) == 0 {
			continue
		}
		for i := len(tokens); i <= 5; i++ {
			tokens = append(tokens, "")
		}

		switch tokens[0] {
		case "PRINT":
			store.Print()
			fmt.Println("==ok==")
		case "STOP":
			return
		case "DELETE":
			if !store.Delete(tokens[1]) {
				fmt.Println("Delete operations failed")
			}
			fmt.Println("==ok==")
		case "ADD":
			n := element{tokens[2], tokens[3], tokens[4]}
			if !store.Add(tokens[1], n) {
				fmt.Println("Add operation failed")
			}
			fmt.Println("==ok==")
		case "LOOKUP":
			n := store.Search(tokens[1])
			if n != nil {
				fmt.Printf("%v\n", n)
			}
			fmt.Println("==ok==")
		case "CHANGE":
			n := element{tokens[2], tokens[3], tokens[4]}
			if !store.Update(tokens[1], n) {
				fmt.Println("Update operation failed")
			}
			fmt.Println("==ok==")
		default:
			fmt.Println("Unknown command - please try again!")
		}
	}

}
