

## Omni协议



![img](https://user-gold-cdn.xitu.io/2019/1/29/16898a4fe9bf0713?imageView2/0/w/1280/h/960/format/webp/ignore-error/1)



Omni协议(之前叫做 Mastercoin),是建立在比特网络上的一个协议.利用 Omni协议,可以很方便的创建代币,现有比特币网络上发行的代币可以在 [Properties for ecosystem Production](https://link.juejin.im?target=https%3A%2F%2Fwww.omniexplorer.info%2Fproperties%2Fproduction) 找到,最知名的就是Tether(USDT).

[Tether（USDT）](https://link.juejin.im?target=https%3A%2F%2Ftether.to%2F)是 `Tether` 公司推出的基于稳定价值货币美元（USD）的代币Tether USD（下称USDT），用户可以随时使用 USDT 与 USD 进行 1:1 兑换。Tether 公司严格遵守 1：1 的准备金保证，即每发行1个 USDT 代币，其银行账户都会有1美元的资金保障。官方称:用户可以在 Tether 平台进行资金查询(现在查不到)





### 真实的USDT转账交易

https://link.juejin.im/?target=https%3A%2F%2Fbtc1.trezor.io%2Ftx%2F0347ab8f6291ab38c233576ddc0a4c3156b96d9fa800b07f2962e35c5b40011c



### OP_RETURN

以 OP_RETURN 开头的锁定脚本有着以下两种含义:

- 这个 vout 不能被花费
- OP_RETURN后面跟随的是备注信息

在上面的 vout2中: `OP_RETURN 6f6d6e69000000000000001f0000000b0f387b00`代表的意义如下:

- 6f6d6e69 : "omni"的ASCII编码,以为这个备注信息是与 Omni 协议有关系的
- 0000 : Transaction version
- 0000 : Transaction type, 2 Bytes,代表着`Simple Send`
- 0000001f : Currency identifier, 4 bytes.  0x1F(十进制的31)是TetherUS 的代号, 如果是测试网则是0x02
  - BTC主网: 1 and 3 to 2,147,483,647
  - BTC测试网: 2 and 2,147,483,651 to 4,294,967,295
- 0000000b0f387b00 : Amount to transfer. 8Bytes. 数量的十六进制0000000b0f387b00 = 47500000000聪 = 475 USDT

| Field               | Type                | Bytes | Example          |
| ------------------- | ------------------- | ----- | ---------------- |
| Transaction version | Transaction version | 2     | 0                |
| Transaction type    | Transaction type    | 2     | 0                |
| Currency identifier | Currency identifier | 4     | 1f               |
| Amount to transfer  | Number of Coins     | 8     | 0000000b0f387b00 |





### 总结

- USDT只是BTC主链的上的代币
- USDT利用OP_RETURN将自己的账本记录在BTC链上
- BTC主链并不会解析OP_RETURN
- USDT自己解析OP_RETURN中的账本信息



### 参考

- https://juejin.im/post/5c5008c26fb9a049bc4d0e20
- 在比特币上发代币的基本原理——omni协议发代币的通俗解释: <https://www.chainnode.com/post/192685>

