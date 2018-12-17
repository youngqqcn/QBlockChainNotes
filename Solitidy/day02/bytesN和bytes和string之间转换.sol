
/*
author:yqq
date:2018-12-17  10:26
desc : solidiy notes
*/

pragma solidity ^0.4.20;




contract C{
    
    bytes5 b5 = 0x0102030405;
    
    bytes public bs5 = new bytes(b5.length);
    
    //bytesN ---> bytes 
    function fixedBytesToBytes(){
        for(uint i =0; i < b5.length; i++){
            bs5[i] = b5[i];
        }
    }
    
    //string--->bytes 
    string public name = "Tom";
    bytes public bsname;
    function stringToBytes(){
        bsname = bytes(name);
    }
    
    //bytes ---> string 
    string public str3 ;
    function bytesToString() public{
        str3 = string(name);
    }
    
    //bytesN ---> string 
    string str4;
    function bytesNToString() public{
        //str4 = string(b5); //error
        //str4 = string(bytes(b5));
        
        
        //bytesN--->bytes--->string
    }
    
    
}