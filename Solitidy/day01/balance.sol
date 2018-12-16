pragma solidity ^0.4.20;


contract AddressBalance{
    
    
    function getBalance(address addr) constant public returns(uint){
        return addr.balance;  //get the addr's balance
    }
    
    
}