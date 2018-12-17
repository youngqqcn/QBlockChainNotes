
/*
author:yqq
date:2018-12-17  12:53 
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract HashAnOwner{
    
    address public owner;
    uint256 public a;
    
    modifier ownerOnly(address addr){
        require(msg.sender == owner);
        _;  //代表修饰器所修饰的函数的代码
    }
    
    function HashAnOwner()    public{
        owner = msg.sender;
    }
    
    function useSuperPowers() ownerOnly(msg.sender) public{
       
        
        a = 10;
    }
    
    
}