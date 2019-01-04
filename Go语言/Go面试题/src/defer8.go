package main


//是否可以编译通过？如果通过，输出什么？

func main() {

	println(DeferFunc1(1))
	println(DeferFunc2(1))
	println(DeferFunc3(1))
}

func DeferFunc1(i int) (t int) {
	t = i
	defer func() {
		t += 3
	}()
	return t
}

func DeferFunc2(i int) int {
	t := i
	defer func() {
		println("llllll")
		t += 3
	}()

	tmpFunc := func() int{
		println("hhhhhh")
		t -= 2
		return t
	}

	return tmpFunc()
}

func DeferFunc3(i int) (t int) {
	defer func() {
		t += i
	}()
	return 2
}



























///  return 先于 defer 执行