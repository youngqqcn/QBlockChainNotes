
/*
author:yqq
date:2018-12-17  12:36 
desc : solidiy notes
*/

pragma solidity ^0.4.20;




contract Test{
    
    uint public v1 = 10;
    uint constant public v2 = 999;
    
    
    
    function f1()  public{
        v1 = 20;
        //v2 = 2222;//error
    }
    
    function f2() constant public{
        v1  = 777; //ok, but not effected
    }
    
    
    //string view str3  = "test"; //error   --> view only for function
    string constant str3 = "test"; //ok    -->constant for variable or function
    
    
    struct Person {
        string name;
        uint age;
    }
    
    function f3() public{
        //Person constant p1; //error
        //Person view P1;//error
        //constant 仅可以修饰值类型, 无法修饰引用类型(string除外)
    }
    
    //pure不能读写变量, 即不可以涉及到合约的成员变量和成员函数
    function f4() pure  public returns(uint){
        //return v1;//error 
		//f2(); //error
		//return 1; //ok
    }
    
}

