pragma solidity ^0.4.17;



contract  Test{
    
    uint[] public    array ;
    
    
    modifier initArray() {
        delete array; //清空数组
        array.push(1);
        array.push(2);
        _;
    }
    
    function test1() initArray public{
        uint[] storage pArray = array;  //引用
        pArray[0] = 999;
    }
    
    function  test2() initArray public{
        uint[] memory  newArray = array; //值传递, 相当于将array中的拷贝到一个新的数组中
        newArray[0] = 444;
    }
    
    //-------------------------------------------------------
    function test3() public initArray{
        test4(array);
    }
    
    function test4(uint []  memArray) public{
        array = memArray;
        changeArray(array);
    }
    
    // 参数是storage类型时，函数必须是private或internal类型的
    function changeArray(uint[] storage arrayTest) internal{
        arrayTest[0] = 666;
    }
    //-------------------------------------------------------
    
    
}