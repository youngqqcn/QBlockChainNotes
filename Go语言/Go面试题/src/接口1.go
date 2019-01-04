

//以下代码能编译过去吗？为什么？


package main

import (
"fmt"
)


type People1 interface {
	Speak(string) string
}
type Stduent struct{}

func (stu *Stduent) Speak(think string) (talk string) {
	if think == "case1" {
		talk = "hello world"
	} else {
		talk = "good"
	}
	return
}

func main() {
	var peo People1 = Stduent{}
	think := "case1"
	fmt.Println(peo.Speak(think))

}


















//定义interface
//
//type VowelsFinder interface {
//	FindVowels() []rune
//}
//
//type MyString string
//
//实现接口
//func (ms MyString) FindVowels() []rune {
//	var vowels []rune
//	for _, rune := range ms {
//		if rune == 'a' || rune == 'e' || rune == 'i' || rune == 'o' || rune == 'u' {
//			vowels = append(vowels, rune)
//		}
//	}
//	return vowels
//}
//
//func main() {
//	name := MyString("Sam Anderson") // 类型转换
//	var v VowelsFinder // 定义一个接口类型的变量
//	v = name
//	fmt.Printf("Vowels are %c", v.FindVowels())
//
//}


//
//
//type People1 interface {
//	Speak(string) string
//}
//type Stduent struct{}
//
//func (stu *Stduent) Speak(think string) (talk string) {
//	if think == "bitch" {
//		talk = "You are a good boy"
//	} else {
//		talk = "hi"
//	}
//	return
//}
//
//func main() {
//	//var peo People1 = Stduent{}
//	//var peo People1 = &Stduent{}
//	var peo People1
//	//var stu2 Stduent
//	stu := Stduent{}
//	peo = &stu     //
//	//stu2 = &stu  //error
//
//
//	//因为 peo 是interface接口类型, 所以可将指针类型赋给它, 又因为Stduent的方法接收者是 *Stduent,
//	// 所以需要将指针赋给它, 如果接收者类型是 Stduent , 即值类型那么原题目就可以编译通过了
//	var it interface{}
//	it = &stu
//	it.(*Stduent).Speak("hahhah")
//
//
//
//	think := "bitch"
//	fmt.Println(peo.Speak(think))
//}



/*
type People1 interface {
	Speak(string) string
}
type Stduent struct{}

func (stu Stduent) Speak(think string) (talk string) {
	if think == "bitch" {
		talk = "You are a good boy"
	} else {
		talk = "hi"
	}
	return
}

func main() {
	//var peo People1 = Stduent{}
	//var peo People1 = &Stduent{}
	var peo People1
	stu := Stduent{}
	peo = stu
	think := "bitch"
	fmt.Println(peo.Speak(think))
}
*/

