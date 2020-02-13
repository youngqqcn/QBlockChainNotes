## XLM 对接文档



### 相关链接:

- 官方文档:https://www.stellar.org/developers/guides/get-started/
- 源码: https://github.com/stellar/stellar-core
- C++(QT)SDK: https://github.com/bnogalm/StellarQtSDK
- 测试实验室: https://www.stellar.org/laboratory/#account-creator?network=test
- PythonSDK: https://github.com/StellarCN/py-stellar-base
- 其他SDK: https://www.stellar.org/developers/reference/
- 测试网区块链浏览器: http://testnet.stellarchain.io/
- 主网区块链浏览器: https://stellarchain.io/



### 如何创建账户

需要让有XLM的账户使用 `CreateAccountOperation`操作进行创建账户,同时可以指定初始金额.



### 普通转账

- 使用 `PaymentOperation`操作即可

- `timebound`设置交易超时时间, 一般设置为 `0`即可, 即表示永远不超时

- 使用text_memo类型进行转账备注即可, 且少于 28 个字符

- `basefee` 使用 100 即可

- 在线获取账户当前的`sequence`, SDK中会在传入的sequence的基础上进行加1

  



