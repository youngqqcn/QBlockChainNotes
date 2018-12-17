/*
author:yqq
date:2018-12-17  10:56 
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract Test{
    
    struct Student{
        string name;
        uint age;
        uint score;
        string gender;
    }
    
    Student stu = Student("yqq", 23, 99, "male");
    Student stu2 = Student({name:"tom", age:19, score:77, gender:"female"});
    
    Student [] public students;
    
    function assign() public{
        students.push(stu);
        students.push(stu2);
        students[0].name="Jack";
    }
    
    
}
