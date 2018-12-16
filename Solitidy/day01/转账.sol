/*
author:yqq
date:2018-12-16  21:51
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract TransferTest{
    
    
    address  acount2 = 0xc6a6FdBcab9eA255eDEE2e658E330a62f793B74E;
    
	//也可以用send来实现
    function transfer() payable public returns(bool){
        acount2.transfer(msg.value);
    }
    
    
}