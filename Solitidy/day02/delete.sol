
/*
author:yqq
date:2018-12-17  12:53 
desc : solidiy notes
*/

pragma solidity ^0.4.20;



/*
 delete操作符可以用于任何变量,将其设置成默认值
 - 如果对string使用delete, 则将字符串的值设为空.
 - 如果对动态数组使用delete,则删除所有元素,其长度变为0
 - 如果对静态数组使用 delete,则重置所有索引的值
 - 如果对map类型使 delete用,什么都不会发生(新版的编译器, 会直接报错)
 - 如果对map类型中的一个键使用delete用,则会删除与该键相关的值
*/


contract  deleteTest{
    
    string public strName = "yqq";
    
    function delStr(){
        delete strName;
    }
    
    function setStr(){
        strName = "Tom";
    }
    
   /*///////////////*/
   
   uint[5] public staticArr = [2, 3, 4, 5, 8];
   uint [] public dynamicArr = new uint[](5);
   
   function initDynArr() public{
       if(dynamicArr.length == 0){
            for (uint i =0; i < 10; i++){
                //dynamicArr[i] = i*10;
                dynamicArr.push(i * 10);
            }
       }else{
            for ( i =0; i < dynamicArr.length; i++){
                dynamicArr[i] = i*10;
                //dynamicArr.push(i * 10);
            }
       }
      
   }
   
   function delStaticArr() public{
       delete staticArr;
   }
   
   function delDynArr() public{
       delete dynamicArr;
   }
   
   function getArrLength() public returns(uint){
       return dynamicArr.length;
   }
   
   
   
   mapping(uint=>string) public map1;
   function initMap() public{
       map1[0] = "yqq";
       map1[2] = "tom";
    
   }
   
   function delMap() public{
       //delete map1; //error
   }
   
   function delMapKey() public{
        delete map1[0]; //ok  , delete  k-v   0 "yqq" 
        map1[0] = "Jack";
   }
   
   
   struct  People{
       string name;
       mapping(string => uint) subScore;  //隐藏在结构体中
       
   }
   
   People public pl;
   function initPl() public{
       pl.name = "yqq";
       pl.subScore["math"] = 80;
   }
   
   function delP1() public{
       delete pl; //ok
   }
   
   function getPScore() public returns(string, uint){
       return (pl.name, pl.subScore["math"]);  //   map还存在
   }
   

   
   
}

