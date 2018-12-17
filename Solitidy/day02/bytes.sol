/*
author:yqq
date:2018-12-17  10:26
desc : solidiy notes
*/

pragma solidity ^0.4.20;




contract C{
    
    
    bytes public  _name = new bytes(1);
    bytes public _name2;
    
    
    function setLength(uint length){
        _name.length = length;
    }
    
    function getLength()constant returns(uint){
        return _name.length;
    }
    
    function setName(bytes name){
        _name = name;
    }
    
    function changeName(bytes1 name){
        _name[0] = name;
    }
    
    function setInside(){
        _name = "helloworld";
        _name2 = "HELLOWORLD";
        
    }
    
    function pushTest(bytes some){
        _name.push(0x99);//ok 
        //_name.push(some); //error
    }
    
}