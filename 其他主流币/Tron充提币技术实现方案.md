## 参考

- 官方API文档:  <https://developers.tron.network/reference>
- C++ <https://github.com/aUscCoder/TronWallet>
- 



## TRON资源模型

>  参考: https://tronprotocol.github.io/documentation-zh/mechanism&algorithm/resource/



- 如果是转账, 目标账户不存在，包括普通转账或发行Token转账，转账操作则会创建账户并转账，只会扣除创建账户消耗的Bandwidth Points，转账**不会**再消耗额外的Bandwidth Points。

- 如果交易需要创建新账户，Bandwidth Points消耗如下：

  - 尝试消耗交易发起者冻结获取的Bandwidth Points。如果交易发起者Bandwidth Points不足，则进入下一步

  - 尝试消耗交易发起者的TRX，这部分烧掉0.1TRX

    > 例如: <https://tronscan.org/#/transaction/f80dacb7b73219b86b45225dc58d7d5337a576ea190899dda5e5ebd3e5de9da5>

- 如果交易是Token转账，Bandwidth Points消耗如下：

  -  依次验证 发行Token资产总的免费Bandwidth Points是否足够消耗，转账发起者的Token剩余免费Bandwidth Points是否足够消耗，Token发行者冻结TRX获取Bandwidth Points剩余量是否足够消耗。如果满足则扣除Token发行者的Bandwidth Points，任意一个不满足则进入下一步

  - 尝试消耗交易发起者冻结获取的Bandwidth Points。如果交易发起者Bandwidth Points不足，则进入下一步

  - 尝试消耗交易发起者的免费Bandwidth Points。如果免费Bandwidth Points也不足，则进入下一步

  - 尝试消耗交易发起者的TRX，交易的字节数 * 10 sun

- 如果交易普通交易，Bandwidth Points消耗如下：

  - 尝试消耗交易发起者冻结获取的Bandwidth Points。如果交易发起者Bandwidth Points不足，则进入下一步

  - 尝试消耗交易发起者的免费Bandwidth Points。如果免费Bandwidth Points也不足，则进入下一步

  - 尝试消耗交易发起者的TRX，交易的字节数 * 10 sun

- 用户的带宽在24小时内恢复, 恢复过程是线性的.(具体公式在官方文档中) 



## TRON 充币技术实现方案



- 获取交易信息:<https://developers.tron.network/reference#transaction-information-by-account-address>

  ```
  curl --request GET \
    --url https://api.trongrid.io/v1/accounts/TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS/transactions
  
  ```




- 获取trc20交易信息: <https://developers.tron.network/reference#trc20-transaction-information-by-account-address>

  ```
  curl --request GET \
    --url https://api.trongrid.io/v1/accounts/TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS/transactions/trc20
  ```

  
  
  
  
- 其他交易费
  
  | 交易类型              | 费用     |
  | --------------------- | -------- |
  | 创建witness(观察节点) | 9999 TRX |
  | 发行token             | 1024 TRX |
  | 创建account           | 0.1 TRX  |
  | 创建exchange          | 1024 TRX |





### 普通TRX交易

`curl -X POST  https://api.trongrid.io/wallet/getblockbynum -d '{"num":14455630}'`



```
{
            "ret": [
                {
                    "contractRet": "SUCCESS"
                }
            ],
            "signature": [
                "16658b4d004737334df951cf8728e03108d3cc2a6ebcad306fb7a4e2984c02fa4bd1ad1664fe4768c36c585171d21207a1fcd8080a075f8b472585f8eaf6a53501"
            ],
            "txID": "f80dacb7b73219b86b45225dc58d7d5337a576ea190899dda5e5ebd3e5de9da5",
            "raw_data": {
                "contract": [
                    {
                        "parameter": {
                            "value": {
                                "amount": 997000000,  
                                "owner_address": "418a4a39b0e62a091608e9631ffd19427d2d338dbd",
                                "to_address": "4195a6569bdccc1bee832803b4116a020950818cba"
                            },
                            "type_url": "type.googleapis.com/protocol.TransferContract"
                        },
                        "type": "TransferContract"
                    }
                ],
                "ref_block_bytes": "933a",
                "ref_block_hash": "ad8de998be3a5ebc",
                "expiration": 1573700973000,
                "timestamp": 1573611260215
            },
            "raw_data_hex": "0a02933a2208ad8de998be3a5ebc40c8e38cbfe62d5a69080112650a2d747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e5472616e73666572436f6e747261637412340a15418a4a39b0e62a091608e9631ffd19427d2d338dbd12154195a6569bdccc1bee832803b4116a020950818cba18c086b4db0370b792a994e62d"
        },
```



其中

```
"value": {
 	"amount": 997000000,  //转账金额,  即 997 TRX
 	
 	"owner_address": "418a4a39b0e62a091608e9631ffd19427d2d338dbd",   
 	                                 //发送地址, 即 TNaRAoLUyYEV2uF7GUrzSjRQTU8v5ZJ5VR
 	                                 
	"to_address": "4195a6569bdccc1bee832803b4116a020950818cba"   
	                                 //接收地址, 即 TPcUx2iwjomVzmX3CHDDYmnEPJFTVeyqqS
}
                         
```







### TRC20交易

同ERC20交易类似



TRC20交易

```
{
            "ret": [
                {
                    "contractRet": "SUCCESS"
                }
            ],
            "signature": [
                "2e0918c8b5c74f9f35f94d03044544f6acd2470024ec7d59f2019c91241a489569901812a789fb10a196f37984b374fe3253807cf1c6b3042f1bac6356bf86ad00"
            ],
            "txID": "7f88b3cae8b2721a2c124bed0af27d7c9f60fad51672756819732779a70a22a0",
            "raw_data": {
                "contract": [
                    {
                        "parameter": {
                            "value": {
                                "data": "a9059cbb0000000000000000000000008a4a39b0e62a091608e9631ffd19427d2d338dbd000000000000000000000000000000000000000000000000000000186d0d8e20",
                                "owner_address": "4136f75d3494f0093d412102853d29b3768735159e",
                                "contract_address": "41a614f803b6fd780986a42c78ec9c7f77e6ded13c"
                            },
                            "type_url": "type.googleapis.com/protocol.TriggerSmartContract"
                        },
                        "type": "TriggerSmartContract"
                    }
                ],
                "ref_block_bytes": "c710",
                "ref_block_hash": "138c16f4dc833693",
                "expiration": 1582009386000,
                "fee_limit": 10000000,
                "timestamp": 1581918923005
            },
```



其中的  `data`的组成和 ERC20转账完全一样

```
函数签名(4字节) + 接受者地址(32字节)  + 金额(32字节)
```

例如上面TRC20-USDT转账

```
a9059cbb   函数签名  即  transfer(address _to, uint256 _value)
0000000000000000000000008a4a39b0e62a091608e9631ffd19427d2d338dbd   #接受者地址
000000000000000000000000000000000000000000000000000000186d0d8e20   #金额
```



其中TRC20的接受者地址是不带`41`的十六进制字符串格式, 即和ETH地址完全一样,  所以, 在转换为 Base58格式的地址形式时需要加上`41`的前缀.