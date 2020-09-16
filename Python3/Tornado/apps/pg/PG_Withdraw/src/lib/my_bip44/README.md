# BIP44 预研

关于BIP32的文章
- https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki

关于BIP44介绍的文章
- https://segmentfault.com/a/1190000017103354
- https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
- https://stevenocean.github.io/2018/09/23/generate-hd-wallet-by-bip39.html

```
m / purpose' / coin_type' / account' / change / address_index
```
>层级说明:  https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki#path-levels

其中的 撇号  表示硬化,  BIP44 固定了只有  purpose , coin_type, account是硬化的

- `m` 为固定
- `purpose` 目前在bip44预定使用44
- `coin_type`：指不通币的种类0代表比特币，1代表比特币测试链，60代表以太坊，恒星币148，EOS194
完整币种类型号列表：https://github.com/satoshilabs
- `account`: 代表账户索引
- `change`：常量0用于外部链，常量1用于内部链，所以0为想被钱包商展示，1不想被钱包商展示
- `address_index` ：这就是地址索引，从0开始，代表生成第几个地址


![](./derivation.png)



已经注册BIP44规范的币种

https://github.com/satoshilabs/slips/blob/master/slip-0044.md