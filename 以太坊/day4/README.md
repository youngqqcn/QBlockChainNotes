# 以太坊学习笔记day4

## 前端框架选择

- 如果你喜欢用（或希望能够用）模板搭建应用，请使用Vue
- 如果你喜欢简单和“能用就行”的东西，请使用Vue
- 如果你的应用需要尽可能的小和快，请使用Vue
- 如果你计划构建一个大型应用程序，请使用React
- 如果你想要一个同时适用于Web端和原生App的框架，请选择React
- 如果你想要最大的生态圈，请使用React
- 如果你已经对其中一个用得满意了，就没有必要换了



## React

- GitHub: https://github.com/facebook/react/

- 学习:http://www.ruanyifeng.com/blog/2015/03/react.html

- 案例学习: https://github.com/ruanyf/react-demos


- react生命周期 : http://www.cnblogs.com/qiaojie/p/6135180.html



##  Vue

https://github.com/vuejs/vue

https://vuejs.org/



## 智能合约安全问题

- 整数溢出
- 数组越界

示例代码:

```
pragma solidity ^0.4.17 ;

/*
author:yqq
data:2018-12-20  22:21 
desc: 溢出共计
*/
//1 weeks = 604800 seconds 
// 2^256 = 115792089237316195423570985008687907853269984665640564039457584007913129639936
//2^-256 - (1 weeks) =  115792089237316195423570985008687907853269984665640564039457584007913129035136

contract TimeLock{
    
    mapping(address => uint) public balance;
    mapping(address => uint) public lockTime;
    
    function deposit() public payable{
        balance[msg.sender] += msg.value;
        lockTime[msg.sender] = now;
        increaseLockTime(1 weeks);
    }
    
    function increaseLockTime(uint _secondsToIncrease) public{
        lockTime[msg.sender] += _secondsToIncrease;
    }
    
    function withdraw() public{
        require(balance[msg.sender] > 0);
        require(now > lockTime[msg.sender]);
        msg.sender.transfer(balance[msg.sender]);
        balance[msg.sender] = 0;
    }
    
}
```

当在increaseLockTime输入: `115792089237316195423570985008687907853269984665640564039457584007913129035136`时就能提取合约中以太币.





> https://www.calculator.net/big-number-calculator.html

## 案例-智能合约彩票项目 

[智能合约彩票项目](./lottery-react/README.md)



