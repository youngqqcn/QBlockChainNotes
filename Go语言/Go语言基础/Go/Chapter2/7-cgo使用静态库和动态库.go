package main


/**
*作者: yqq
*日期: 2018/11/29  17:05
*描述: 使用动态库


//关于(gcc g++)下 制作动态库
http://www.cnblogs.com/jiqingwu/p/linux_dynamic_lib_create.html
gcc *.c -fPIC -shared -o libxxxxx.so
gcc *.c -fPIC -shared -o libxxxxx.dll  (windows)

//关于(gcc g++)制作静态库
gcc  *.c  -c -o  xxxx.o
ar   rs  xxxx.a  xxx.o
ar   rs  xxxx.lib  xxx.o   (windows)

*/

// #include "winlin.h"
// #cgo LDFLAGS: ${SRCDIR}/动态库和静态库/winlin.lib -lstdc++
import "C"
import "fmt"


//或
// #cgo LDFLAGS: ${SRCDIR}/动态库和静态库/winlin.so -lstdc++
//使用静态库
// #cgo LDFLAGS: ${SRCDIR}/动态库和静态库/winlin.lib -lstdc++
// #cgo LDFLAGS: ${SRCDIR}/动态库和静态库/winlin.a-lstdc++

func main() {
	fmt.Println("version is", C.winlin_version())
}
