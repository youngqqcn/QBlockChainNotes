pragma solidity ^0.4.20;

contract BoolTest{
    
    bool bFlag = false;
    
    
    function getFlag() view public returns(bool){
        return bFlag;
    }
    
    function getFlag2() view public returns(bool){
        return !bFlag;
    }
    
}