pragma solidity ^0.4.17 ;

/*
author:yqq
data:2018-12-19  14:58
desc: array test 
*/


contract C{
    
    int []  public array;
    
    string public message;
    
    function C(string _message) public{
        message = _message;
    }
    
    function put(int i) public{
        array.push(i);
    }
    
    function getArray() public view returns(int []){
        return array;
    }
    
    function getArrayLength() public view returns(uint){
        return array.length;
    }
    
    
    //多个返回值
    function getMulRet() public view returns(uint, string){
        return (array.length, "hahha");
    }
    
}