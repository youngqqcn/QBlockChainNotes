package main

/**
*作者: yqq
*日期: 2019/1/4  14:19
*描述:
*/







func main() {


	var i = 0
	RESTART:
		i++
		if i == 3{
			goto END

		}


	defer func() {
		LOOP:
			//goto RESTART
			println("hello")
		goto LOOP
	}()

	goto RESTART

	END:


}
