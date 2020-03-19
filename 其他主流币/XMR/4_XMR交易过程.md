## XMR交易过程



### 参考文档

> - [深入探究门罗币与密码学](https://medium.com/@WooKeyWallet/精通门罗币-第5章-深入探究门罗币与密码学-下篇-3dedd99f75bf)
> - [门罗币的环签名分析]([https://github.com/XChainLab/documentation/blob/master/privacy/%E9%97%A8%E7%BD%97%E5%B8%81%E3%80%81ZEC%E5%92%8C%E8%BE%BE%E4%B8%96%E5%B8%81%E7%9A%84%E5%AF%B9%E6%AF%94%E5%88%86%E6%9E%90%E4%B9%8B%E4%BA%8C%E9%97%A8%E7%BD%97%E5%B8%81%E7%9A%84%E7%8E%AF%E7%AD%BE%E5%90%8D%E5%88%86%E6%9E%90.md](https://github.com/XChainLab/documentation/blob/master/privacy/门罗币、ZEC和达世币的对比分析之二门罗币的环签名分析.md))



### 名词解析

- *Ring Signature*: 环签名,  使用签名者的公钥和其他人的公钥进行混合, 再用一次性私钥进行签名

- *RingCT  ( Ring  Confidential  Transaction)*: 环机密交易, 用于隐藏真实的转账金额

- *key-image* :  用判断是否是双花
- *Stealth (one-time) Addresses*:  隐匿地址(一次性)





### XMR交易流程图

![](./img/XMR_tx.png)



- 1,  2, 3 , 4  :  生成 一次性私钥
- 5, 6, 7, 8, 9  : 生成隐匿输出公钥 
- 10  :将真实的TXO(交易输出) 与其他人的TXO进行混合
- 11  :刚生成的一次私钥对应的公钥和上一笔交易输出的隐匿输出公钥相等
- 12, 13,  14 : 使用一次性私钥进行环签名,   每笔交易的key-image是唯一的以防止双花

- 15: 将环签名附加在交易结构后面



