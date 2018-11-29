package main



/*
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct  _Stu{
	char *pszName;
}Stu;

char MyToUpper(char in)
{
	if('a'<= in && in <= 'z') //如果时小写， 转为大写
		return in - ('a'-'A');
	return in;
}


*/
import "C"
import "unsafe"
import "fmt"



func main(){

	var t C.Stu
	//var s = "hello world"


	t.pszName = (*C.char)(C.malloc(C.size_t(100)))
	if  t.pszName == nil{
		panic("malloc failed!\n")
	}
	//如果分配内存成功
	defer C.free(unsafe.Pointer(t.pszName)) //释放内存	


	//将go的字符串转为c的字符串
	var ch *C.char = C.CString("golang")
	defer C.free(unsafe.Pointer(ch))

	//调用
	C.strcpy(t.pszName, ch)
	fmt.Println(C.GoString(t.pszName)) //将C的字符串转为go string

	var pTmp *C.char 
	for i := C.size_t(0); i < C.strlen(t.pszName); i++{
		pTmp  = (*C.char)( unsafe.Pointer( uintptr(unsafe.Pointer(t.pszName)) + uintptr(i) ))
		*pTmp = C.char(C.MyToUpper(C.char(*pTmp)))
	}

	fmt.Println(C.GoString(t.pszName))
}
