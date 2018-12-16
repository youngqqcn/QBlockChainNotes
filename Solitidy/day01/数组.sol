/*
author:yqq
date:2018-12-17 00:11 
desc : solidiy notes
*/

pragma solidity ^0.4.20;


//定长数组
contract fixedArray{
    
    bytes1 b1 = "y";
    bytes2 b2 = "xy";
    bytes3 public b3 = '1';
    uint256 public len = b3.length; //3 
    
   // b3[0] = "9"; //error 
   
   bytes1 public bb1 = b1[0];
}



//数组
contract test1{
    
    uint public len = 0;
    function func(){
        //memory
        uint[] memory values = new uint[](10);
        values[0] = 1;
       // values.push(1);
        len = values.length;
    }
    
    //storage
    uint[] public arr;
    uint public arrlen = 0;
    function func2(){
        arr = new uint[](10); 
        arr[0] = 99;
        arr.push(999); //ok
        arr.length  = 99999;
        arrlen = arr.length;
        
    }
    
}

contract test2{
    
    
    uint[5] arr3 = [1, 2, 3, 4, 5];
    uint public sum =0 ;
    function  fun3(){
        arr3[0] = 0;
        uint a = arr3[1];
        
        for(uint i = 0 ; i < arr3.length; i++){
            sum += arr3[i];
        }
        
        //arr3.push(89);//error
    }
}











