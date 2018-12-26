### Chaincode 理解

这两天研究Fabric, 看了一两个Chaincode的例子, 对Chaincode有疑惑: 

> Chaincode只是对K-V数据库的增删改查?

看过几篇文章之后, 结合对以太坊的智能合约的理解. 我得出以下结论:

> 智能合约的作用就是对数据库进行增删改查. 
>
> - 在以太坊中数据存储在公链上; 
> - Hyperledger Fabric中数据存储在Peer点的数据库(LevelDB或CouchDB)中.



### System Chaincode

System Chaincode在peer进程中运行，不像普通的chaincode是在一个单独的容器中运行. System Chaincode分为以下几种:

- LSCC（ Lifecycle system chaincode ）：生命周期系统chaincode处理上面描述的生命周期请求

- CSCC（Configuration system chaincode）：配置系统chaincode在peer端处理channel配置

- QSCC（Query system chaincode）：查询系统chaincode提供了分类查询api，例如获取块和事务

- ESCC（Endorsement system chaincode）：背书系统chaincode通过签署事务提案响应来处理支持

- VSCC（Validation system chaincode）：验证系统chaincode处理事务验证，包括检查背书策略和多版本并发控



### Fabric1.0中Peer维护的4个DB

-  id store，存储 chainID
- stateDB，存储 world state ,  在记账节点committing时, 会将world state 写入 stateDB中.
- versionDB，存储 key 的版本变化
- blockDB，存储 block





### 参考

- https://blog.csdn.net/sun13465816527/article/details/80452437

- https://blog.csdn.net/qq_40012404/article/details/81513906

- http://www.mumayi.com/xinwen-20180205-63814.html