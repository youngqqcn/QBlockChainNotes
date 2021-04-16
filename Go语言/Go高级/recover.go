package main

// func main() {
// 	fmt.Println("a")
// 	if err := recover(); err != nil {
// 		fmt.Println(err)
// 	}

// 	panic("panic")
// 	fmt.Println("b")
// 	if err := recover(); err != nil {
// 		fmt.Println(err)
// 	}
// 	fmt.Println("c")
// }

// func main() {
// 	fmt.Println("a")
// 	defer func() {
// 		func() {
// 			if err := recover(); err != nil {
// 				fmt.Println("b")
// 				fmt.Println(err)
// 			}
// 			fmt.Println("c")
// 		}()
// 	}()

// 	panic("panic")

// 	fmt.Println("d")
// }

// func main() {
// 	fmt.Println("a")
// 	defer func() {
// 		fmt.Println("m")
// 	}()

// 	defer func() {
// 		defer func() {
// 			fmt.Println("n")
// 		}()

// 		if err := recover(); err != nil {
// 			fmt.Println("b")
// 			fmt.Println(err)
// 		}
// 		fmt.Println("c")

// 		defer func() {
// 			fmt.Println("o")
// 		}()
// 	}()

// 	defer func() {
// 		fmt.Println("x")
// 	}()

// 	panic("panic")

// 	fmt.Println("d")
// }

// func main() {
// 	fmt.Println("a")
// 	defer func() {
// 		defer func() {
// 			if err := recover(); err != nil {
// 			fmt.Println("b")
// 			fmt.Println(err)
// 			}
// 		}()
// 	}()

// 	panic("panic")

// 	fmt.Println("d")
// }

// func main() {
// 	fmt.Println("a")
// 	defer func() {
// 		func() {
// 			if err := recover(); err != nil {
// 				fmt.Println("b")
// 				fmt.Println(err)
// 			}
// 			fmt.Println("c")
// 		}()
// 	}()

// 	panic("panic")

// 	fmt.Println("d")
// }

// func main() {
// 	// 无法捕获异常
// 	defer recover()
// 	panic(1)
// }

func myfunc() {
	recover()
}

func main() {

	defer myfunc() 

	panic("errrrrrrrrror")

}