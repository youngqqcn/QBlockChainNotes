/*
author:yqq
date:2018-12-16  21:51
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract addressThis {
    
    uint _money;
    
    //payable 
    function addressThis() payable public{
        _money = msg.value;  
    }
    
    function getMoney() view public returns(uint){
        return _money;
    }
    
    
    function getThis() view returns(address){
        return this ; //this is the contract 
    }
    
    function getBalance() view public returns(uint256){
        return this.balance;
    }
    

}