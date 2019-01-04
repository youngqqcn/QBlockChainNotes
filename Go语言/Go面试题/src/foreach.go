package main

import "fmt"


//运行结果是怎样?

type student struct {
	Name string
	Age  int
}

func pase_student() {
	m := make(map[string]*student)
	stus := []student{
		{Name: "zhou", Age: 24},
		{Name: "li", Age: 23},
		{Name: "wang", Age: 22},
	}
	for _, stu := range stus {
		m[stu.Name] = &stu
	}

	for key, value := range m{
		fmt.Println(key, ":" ,value)
	}

}

func main() {

	pase_student()

}


































/*
type student struct {
	Name string
	Age  int
}

func pase_student() {
	m := make(map[string]*student)
	stus := []student{
		{Name: "zhou", Age: 24},
		{Name: "li", Age: 23},
		{Name: "wang", Age: 22},
	}


	for _, stu := range stus {
		fmt.Printf("%p\n", &stu)    //都是副本,都是同一块地址
		m[stu.Name] = &stu
	}


	for key, value := range m{
		fmt.Println(key, "==>", value)
	}
}

func main()  {
	pase_student()
}
*/