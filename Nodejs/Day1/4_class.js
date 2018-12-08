
//继承

class Person{

    constructor(name) {
        this.name = name;
        console.info("Person 构造函数", name)
    }


    say(){
        console.log(`name:${this.name}`) //raw string

    }

}


class Stu extends  Person{


    say(){
        console.log(`stu name:${this.name}`) //raw string

    }

}


var person = new Person("yqq") ;
person.say();

let stu = new Stu("stu1");
stu.say();


