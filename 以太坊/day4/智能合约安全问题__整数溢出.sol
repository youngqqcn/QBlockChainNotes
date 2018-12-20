pragma solidity ^0.4.17 ;

/*
author:yqq
data:2018-12-20  22:21 
desc: 溢出共计
*/
//1 weeks = 604800 seconds 
// 2^256 = 115792089237316195423570985008687907853269984665640564039457584007913129639936
//2^-256 - (1 weeks) =  115792089237316195423570985008687907853269984665640564039457584007913129035136

contract TimeLock{
    
    mapping(address => uint) public balance;
    mapping(address => uint) public lockTime;
    
    function deposit() public payable{
        balance[msg.sender] += msg.value;
        lockTime[msg.sender] = now;
        increaseLockTime(1 weeks);
    }
    
    function increaseLockTime(uint _secondsToIncrease) public{
        lockTime[msg.sender] += _secondsToIncrease;
    }
    
    function withdraw() public{
        require(balance[msg.sender] > 0);
        require(now > lockTime[msg.sender]);
        msg.sender.transfer(balance[msg.sender]);
        balance[msg.sender] = 0;
    }
    
}