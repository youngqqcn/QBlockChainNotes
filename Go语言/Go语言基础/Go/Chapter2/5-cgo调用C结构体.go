package main

/*
   typedef struct _POINT{
		double x;
		double y;
   }POINT;
*/
import "C"
import "fmt"


func main(){
	var p C.POINT
	p.x = C.double(9.244)
	p.y = C.double(9.23)

	fmt.Println(p)
}
