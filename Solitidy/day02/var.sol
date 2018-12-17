/*
author:yqq
date:2018-12-17  11:10 
desc : solidiy notes
*/

pragma solidity ^0.4.20;


contract C{
    
    //0.5.1  disallow 'var' 
    function loopTest() pure{
        for(var i= 0; i < 1000; i++){
            
        }
    }
    
   // var public strName = "yqq";  //error 
   
//   function func(){
//       string storage strName = "yqq";
//       var str2 = strName;
//   }
}