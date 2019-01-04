package main


func test2(x int) (func(),func())  {
	return func() {
		println(x)
		x+=10
	}, func() {
		println(x)
	}
}

func main()  {
	a,b:=test2(100)
	a()
	b()
}

