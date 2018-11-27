package main

import "fmt"

/**
*作者: yqq
*日期: 2018/11/27  21:38
*描述: map 及 其操作

	map 和  C++中STL中的 map
            python中的 dict
         类似

	在Go语言中  map做函数参数, 是引用传递

*/

func main() {

	var map1 map[int]string = map[int]string{1:"yqq", 2:"Tom", 3:"Jim"}
	fmt.Println(map1)
	for k, v := range map1{
		fmt.Printf("%d-->%s\n", k, v)
	}

	fmt.Println("=================")
	map2 := map[int]string{0:"China", 1:"USA", 3:"France"}
	for k, v := range map2{
		fmt.Printf("%d-->%s\n", k, v)
	}

	fmt.Println("=================")
	map2[1] = "Spain"
	for k, v := range map2{
		fmt.Printf("%d-->%s\n", k, v)
	}


	fmt.Println("=================")
	delete(map2,  3)
	map2[1] = "Spain"
	for k, v := range map2{
		fmt.Printf("%d-->%s\n", k, v)
	}

	////////////////////////////
	fmt.Println("=========================")
	map3 := map[int]string{0:"jj", 1:"kk", 2:"ll", 3:"zz"}
	fmt.Println(map3)
	DelMap(map3, 3)
	fmt.Println(map3)

	map3[9] = "9999"
	fmt.Println(map3)

	fmt.Println("===========================")
	Insert(map3, 100, "100")
	fmt.Println(map3)
	fmt.Println("===========================")
	InsertPlus(&map3, 5555, "5555")
	fmt.Println(map3)

}

func Insert(m map[int]string , key int , value string)   {
	m[key] = value
}

//使用指针传递
func InsertPlus(pMap *map[int]string , key int , value string)   {
	(*pMap)[key] = value
}

func DelMap(m  map[int]string, key int)  {
	delete(m, key)
}
