 /*
author:yqq
date:2018-12-16  23:49
desc : solidiy notes
*/

pragma solidity ^0.4.20;

contract functionTest{
    uint256  public v1;
    uint256 public v2;
    
    
    function internalFunc() internal {
        v1 = 999;    
    }
    
    function externalFunc() external returns(uint256){
        v2 = 333;
        return v2;
    }
    
    function resetV2() public{
        v2 = 0;
    }
    
    function callFunc(){
        
        internalFunc(); //ok 
       
        //externalFunc();//error
        
        //this.internalFunc(); //error , 相当于外部调用
        this.externalFunc(); //ok
    }
}

contract Son is functionTest{  //可以继承internal修饰的函数
    function callInternalFunc() public{
        internalFunc(); //ok 
        //externalFunc() ;///error
        this.externalFunc();//ok
    }
}

contract Other{
    uint256  public v3;
    function externalCall(functionTest obj){   //调用的时候, 需要传functionTest合约的地址
        v3 = obj.externalFunc(); //调用另一个合约的外部函数
        //obj.internalFunc();//error 不能调用另外一个合约的内部函数
    }
    
}











