/*
author:yqq
date:2018-12-16  21:44 
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract senderTest{
    
    address public _owner;
    
    
    function senderTest()  public{
        _owner = msg.sender;           //get the sender's addr by the global variable 'msg'
        //if change the account , the msg.sender do not change ! but the invoker will change!
    }
    
    function getOwnerBalance() constant  public returns(uint256){
        return msg.sender.balance;      //get the sender's balance 
    }
    
    function getInvoker() view public returns(address){
        return msg.sender;
    }
    
    
}