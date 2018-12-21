# 以太坊学习笔记day5



## storage和memory

>  https://solidity.readthedocs.io/en/v0.4.21/types.html#data-location

Every complex type, i.e. *arrays* and *structs*, has an additional annotation, the “data location”, about whether it is stored in memory or in storage. Depending on the context, there is always a default, but it can be overridden by appending either `storage` or `memory` to the type. The default for function parameters (including return parameters) is `memory`, the default for local variables is `storage` and the location is forced to `storage` for state variables (obviously).

```
每个复杂的类型, 例如: 数组和结构体, 都额外有一个声明,叫做"数据存储位置"来指定存储在内存还是硬盘.到底存储在哪, 默认情况下取决于上下文, 但是可以用`storage`和 `memory`来显示声明.函数的参数和函数的返回值默认都是`memory`, 而局部变量默认是`storage`, 并且状态变量必须是`storage`.
```

There is also a third data location, `calldata`, which is a non-modifiable, non-persistent area where function arguments are stored. Function parameters (not return parameters) of external functions are forced to `calldata` and behave mostly like `memory`.

```
第三种`数据存储位置`叫做`calldata`, 它是只读的, 临时的区域, 用来存储函数的参数.外部函数的参数被强制设置为`calldata`,并且看上去和`memory`一样.
```

Data locations are important because they change how assignments behave: assignments between storage and memory and also to a state variable (even from other state variables) always create an independent copy. Assignments to local storage variables only assign a reference though, and this reference always points to the state variable even if the latter is changed in the meantime. On the other hand, assignments from a memory stored reference type to another memory-stored reference type do not create a copy.

```
`数据存储位置`很重要, 因为它关系到改变和赋值的操作: `storage`和`memory`之间的赋值都会创建一个独立的copy; `storage`之间的赋值仅仅是引用传递, 所引用的对象后期可能会发生改变. 另一方面, 两个`memory`之间的赋值, 则不会创建新的copy.
```

#### Summary

- Forced data location:

  parameters (not return) of external functions: calldatastate variables: storage

- Default data location:

  parameters (also return) of functions: memoryall other local variables: storage

- new出来的数组是 `memory`	



```sol
//官方文档
pragma solidity ^0.4.0;

contract C {
    uint[] x; // the data location of x is storage

    // the data location of memoryArray is memory
    function f(uint[] memoryArray) public {
        x = memoryArray; // works, copies the whole array to storage
        var y = x; // works, assigns a pointer, data location of y is storage
        y[7]; // fine, returns the 8th element
        y.length = 2; // fine, modifies x through y
        delete x; // fine, clears the array, also modifies y
        // The following does not work; it would need to create a new temporary /
        // unnamed array in storage, but storage is "statically" allocated:
        // y = memoryArray;
        // This does not work either, since it would "reset" the pointer, but there
        // is no sensible location it could point to.
        // delete y;
        g(x); // calls g, handing over a reference to x
        h(x); // calls h and creates an independent, temporary copy in memory
    }

    function g(uint[] storage storageArray) internal {}
    function h(uint[] memoryArray) public {}
}
```



测试代码

```
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
```





## 智能合约效率问题

```
 function approveRequest(uint nArrayIndex) public{
        require(nArrayIndex < payRequests.length);
        PayRequest storage request = payRequests[nArrayIndex];
        
        //消耗大量gas
        for(uint i = 0; i < addrPlayers.length; i++){
            if(addrPlayers[i] == msg.sender) {
                break;
            }
            if(i == addrPlayers.length - 1 /* && addrPlayers[i] != msg.sender*/){
                require(false);
            }
        }
        
        //消耗大量gas
        for(i =0; i < request.vctVotedAddr.length; i++){
            if(msg.sender == request.vctVotedAddr[i]){
                require(false);
            }
        }
        
        request.nAgreeCount += 1;
        request.vctVotedAddr.push(msg.sender);
    }
```

优化后

```
   function approveRequest(uint nArrayIndex) public{
        require(nArrayIndex < payRequests.length);
        PayRequest storage request = payRequests[nArrayIndex];
       
        require(mapPlayer[msg.sender]);
        require(payRequests[nArrayIndex].mapVote[msg.sender] == false);
        request.nAgreeCount += 1;
        payRequests[nArrayIndex].mapVote[msg.sender] = true;
    }
```



## 案例: 众筹

```
pragma solidity ^0.4.17;


//用智能合约部署智能合约
contract FundingFactory{
    
    address[] public fundings; 
    
    function deploy(string _strProName, uint _nSupportMoney, uint _nGoalMoney) public{
        address funding = new Funding(_strProName, _nSupportMoney , _nGoalMoney, msg.sender);
        fundings.push(funding);
    }
    
}


contract Funding{
    
    bool bSuccessFlag = false;
    address public addrManager;
    string public strProjectName;
    uint public nSupportMoney;
    uint public nEndTime;
    uint public nGoalMoney;
    address []  public addrPlayers;
    mapping(address=>bool)  mapPlayer;  //使用mapping提高效率, 降低gas消耗
    
    
    PayRequest[]   public payRequests;  //付款请求结构体
    
    struct PayRequest{
        string  strDesc;
        uint    nPayment; //out 
        address addrShop;
        bool   bCompleted;
        mapping(address=>bool) mapVote;
        //address[] vctVotedAddr;
        uint  nAgreeCount; 
    }
    
    modifier onelyManager(){
        //require(bSuccessFlag);
        require(msg.sender == addrManager);
        _;
    }
    
    
    function   createRequest(string  _strDesc, uint _nPayment, address _addrShop) public onelyManager{
        PayRequest memory  payRequest =   PayRequest({
            strDesc : _strDesc,
            nPayment : _nPayment,
            addrShop : _addrShop,
            bCompleted : false,
            nAgreeCount : 0
        });
        
        payRequests.push(payRequest);
        
    }
    
    
    function Funding(string _strProName, uint _nSupportMoney, uint _nGoalMoney, address _manager) public{
        addrManager = _manager;//msg.sender;
        strProjectName = _strProName;
        nSupportMoney = _nSupportMoney;
        nGoalMoney = _nGoalMoney;
        nEndTime = now + 4 weeks;
       
    }
    
    function getBalance() view public returns(uint){
        return this.balance;
    }
    
    
    function getPlayersCount()public view returns(uint){
        return addrPlayers.length;
    }
    
    function getPlayers() public view returns(address[]){
        return addrPlayers;
    }
    
    function getRemainSeconds() public view returns(uint){
        return (nEndTime - now) ; //seconds
    }
    
    
    function checkStatus() view public{
        require(bSuccessFlag == false);
        require(now > nEndTime);
        require(this.balance > nGoalMoney);
    }
    
    function support() payable public{
        require(msg.value >= 50 wei);
        nSupportMoney += msg.value;
        addrPlayers.push(msg.sender);
        mapPlayer[msg.sender] = true;
    }
    
    function approveRequest(uint nArrayIndex) public{
        require(nArrayIndex < payRequests.length);
        PayRequest storage request = payRequests[nArrayIndex];
       
        require(mapPlayer[msg.sender]);
        require(payRequests[nArrayIndex].mapVote[msg.sender] == false);
        request.nAgreeCount += 1;
        payRequests[nArrayIndex].mapVote[msg.sender] = true;
    }
    
    
    
    // function approveRequest(uint nArrayIndex) public{
    //     require(nArrayIndex < payRequests.length);
    //     PayRequest storage request = payRequests[nArrayIndex];
        
    //     for(uint i = 0; i < addrPlayers.length; i++){
    //         if(addrPlayers[i] == msg.sender) {
    //             break;
    //         }
    //         if(i == addrPlayers.length - 1 /* && addrPlayers[i] != msg.sender*/){
    //             require(false);
    //         }
    //     }
        
        
    //     for(i =0; i < request.vctVotedAddr.length; i++){
    //         if(msg.sender == request.vctVotedAddr[i]){
    //             require(false);
    //         }
    //     }
        
    //     request.nAgreeCount += 1;
    //     request.vctVotedAddr.push(msg.sender);
    // }
    
    
    
    function finilizeRequest(uint nRequestIndex) public{
        PayRequest storage requst = payRequests[nRequestIndex];
        require(requst.bCompleted == false);
        require(requst.nAgreeCount * 2 > addrPlayers.length);
        
        
        //付款
        require(this.balance > requst.nPayment);
        requst.addrShop.transfer(requst.nPayment);
        requst.bCompleted = true;
    }
    
    
    
}
```

