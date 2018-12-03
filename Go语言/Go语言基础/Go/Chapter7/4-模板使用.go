package main

import (
	"os"
	"text/template"
)

/**
*作者: yqq
*日期: 2018/12/3  16:17
*描述:
	模板使用



https://github.com/astaxie/build-web-application-with-golang/blob/master/zh/07.4.md

Go语言的模板通过{{}}来包含需要在渲染时被替换的字段，{{.}}表示当前的对象，
这和Java或者C++中的this类似，如果要访问当前对象的字段通过{{.FieldName}}，
但是需要注意一点：这个字段必须是导出的(字段首字母必须是大写的)，否则在渲染的时候就会报错


{{range}} 这个和Go语法里面的range类似，循环操作数据
{{with}}操作是指当前对象的值，类似上下文的概念



*/




func main() {
	tEmpty := template.New("template test")
	tEmpty = template.Must(tEmpty.Parse("空 pipeline if demo: {{if ``}} 不会输出. {{end}}\n"))
	tEmpty.Execute(os.Stdout, nil)

	tWithValue := template.New("template test")
	tWithValue = template.Must(tWithValue.Parse("不为空的 pipeline if demo: {{if `anything`}} 我有内容，我会输出. {{end}}\n"))
	tWithValue.Execute(os.Stdout, nil)

	tIfElse := template.New("template test")
	tIfElse = template.Must(tIfElse.Parse("if-else demo: {{if `anything`}} if部分 {{else}} else部分.{{end}}\n"))
	tIfElse.Execute(os.Stdout, nil)
}





/*
//2.输出嵌套字段内容
type Friend struct {
	Fname string
}

type Person struct {
	UserName string
	Emails   []string
	Friends  []*Friend
}


func main() {
	f1 := Friend{Fname: "youngqq.cn"}
	f2 := Friend{Fname: "Tom"}
	t := template.New("fieldname example")
	t, _ = t.Parse(`hello {{.UserName}}!
			{{range .Emails}}
				an email {{.}}
			{{end}}
			{{with .Friends}}
			{{range .}}
				my friend name is {{.Fname}}
			{{end}}
			{{end}}
			`)
	p := Person{UserName: "yqq",
		Emails:  []string{"yqq@163.com", "youngqccn@126.com"},
		Friends: []*Friend{&f1, &f2}}
	t.Execute(os.Stdout, p)
}
*/




//字段操作
/*
type Person struct {
	UserName string

}

func main() {

	t := template.New("template test")
	t,  _ = t.Parse("hello {{.UserName}}!")
	p := Person	{UserName:"yqq"}
	t.Execute(os.Stdout, p)

}
*/
