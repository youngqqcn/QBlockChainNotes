
/*
author:yqq
date:2018-12-17  12:48  
desc : solidiy notes
*/

pragma solidity ^0.4.20;



contract HashAnOwner{
    
    address public owner;
    uint256 public a;
    
    
    function HashAnOwner()    public{
        owner = msg.sender;
    }
    
    function useSuperPowers() public{
        require(msg.sender == owner);
        
        /*
        if(msg.sender  != owner){
            throw;
        }*/
        
        a = 10;
    }
    
    
}