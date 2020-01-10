# ERC20智能合约评估

参考:  https://github.com/slowmist/Knowledge-Base/blob/master/solidity-security-comprehensive-list-of-known-attack-vectors-and-common-anti-patterns-chinese.md 



## ERC20标准接口

```
//代币名字
function name() constant returns (string name) 

//代币简称
function symbol() constant returns (string symbol)

//支持几位小数点后几位, balanceOf返回的值除以此值才是真正的余额
function decimals() constant returns (uint8 decimals)

//发行代币的总量
function totalSupply() constant returns (uint256 totalSupply)

//输入地址，可以获取该地址代币的余额。
function balanceOf(address _owner) constant returns (uint256 balance)

//调用transfer函数将自己的token转账给_to地址，_value为转账个数
function transfer(address _to, uint256 _value) returns (bool success)


//--------------------------------------------
//批准_spender账户从自己的账户转移_value个token。可以分多次转移。
function approve(address _spender, uint256 _value) returns (bool success)

//与approve搭配使用，approve批准之后，调用transferFrom函数来转移token。
function transferFrom(address _from, address _to, uint256 _value) returns (bool success)

//返回_spender还能提取token的个数。
function allowance(address _owner, address _spender) constant returns (uint256 remaining)


```





### 标准接口代码实现常见漏洞

可以参考  https://www.jianshu.com/p/2705e5c53ec9 





#### transferFrom

-  没有校验 `allowed[_from][msg.sender] > _value `, 导致可以转账`_from` 中所有的币, 如:  https://cn.etherscan.com/address/0xa0872ee815b8dd0f6937386fd77134720d953581#code 
- 没有使用 SafeMath 库,  直接使用 `*`(乘号) , `/`(除号) , 导致整数溢出.  如 https://cn.etherscan.com/address/0xc5d105e63711398af9bbff092d4b6769c82f793d#code 









## 常见漏洞

### 整数溢出

