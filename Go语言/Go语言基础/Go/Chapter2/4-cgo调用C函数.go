package main


/*
#include <stdio.h>
int Add(int a, int b)
{
	return a + b;
}
*/
import "C"
import "fmt"

func main(){
	var a, b int = 10, 11
	result := int(C.Add(C.int(a), C.int(b)))
	fmt.Println(result)
}
