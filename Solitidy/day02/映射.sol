/*
author:yqq
date:2018-12-17  11:02
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract C{
    
    //id-->name
    
    mapping(uint=>string) id_names;
    
    function C() public{
        id_names[0x1] = "yqq";
        id_names[2] = "Tom";
        id_names[1] = "Jack";
    }
    
    function getNameById(uint id) constant public returns(string){
        string  name = id_names[id];
        return name;
    }
    
    
    
    
}
