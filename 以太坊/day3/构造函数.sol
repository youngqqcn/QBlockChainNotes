pragma solidity ^0.5.1 ;


contract Test{
    
    string public message;
    
    constructor (string memory _message) public{
        message = _message;
    }
    
}