package main

import "fmt"


func addOne(a []*int) {
	for i, p := range a {
		fmt.Printf("i=%d\n", i)
		*p += 1
	}
}

func main() {

	// *int   	: pointer to int
	// []int 	: array of int
	// []*int 	: array of  *int
	//  *[]*int	: pointer to array of *int
	//
	// **int  	: pointer to pointer to int
	//
	// type Calc func(int)

	var x int = 5
	var y int = 7

	// 数组(切片)指针相关
	var a []*int = []*int{&x, &y}
	var pa *[]*int = &a

	addOne(a)

	for i, p := range a {
		fmt.Printf("%d, %d\n", i, *p)
	}

	fmt.Printf("pa = %v\n", pa)
	for i, p := range *pa {
		fmt.Printf("%d, %d\n", i, *p)
	}

	// 多级指针相关
	var px *int = &x
	var ppx **int = &px
	fmt.Printf("px = %v, *px = %d\n", px, *px)
	fmt.Printf("ppx = %v, *ppx = %v\n", ppx, *ppx)


	// 函数指针相关
	var cs CalcVec = CalcVec{CalcA, CalcB, CalcC}
	var pcs CalcVecPointer = &cs
	call(pcs)
}


type Calc func(int)          // func
type CalcVec []Calc          // array of func
type CalcVecPointer *CalcVec // pointer to array of func

func CalcA(n int) {
	fmt.Printf("A+++++++++> %d\n", n)
}

func CalcB(n int) {
	fmt.Printf("B---------> %d\n", n)
}

func CalcC(n int) {
	fmt.Printf("C=========> %d\n", n)
}

func call(calcs CalcVecPointer) {
	for _, calc := range *calcs {
		calc(999)
	}
}
