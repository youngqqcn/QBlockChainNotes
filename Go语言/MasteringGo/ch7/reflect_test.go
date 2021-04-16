package reflect_test

import (
	"fmt"
	"reflect"
	"testing"
)

func TestReflect(t *testing.T) {

	x := 99
	refl := reflect.ValueOf(&x).Elem()
	fmt.Printf("%v\n", refl.Type().String())
	fmt.Printf("%v\n", reflect.TypeOf(x).String())

}
