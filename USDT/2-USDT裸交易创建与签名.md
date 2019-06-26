> [TOC]
>
> 

## 1.USDT简单的裸交易



### 1.1.列出BTC的UTXO

```
omnicore-cli  -conf=/root/.bitcoin/bitcoin-test.conf listunspent  0 99999 [\"mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE\"]


{
    "txid": "5edeaf9f9a628bbfb00c08bba62f4ec8e1f3c87f8ee96261a80668e44413bec3",
    "vout": 0,
    "address": "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE",
    "account": "pluto",
    "scriptPubKey": "76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac",
    "amount": 0.01000000,
    "confirmations": 2,
    "spendable": true,
    "solvable": true
 }
```



### 1.2.创建BTC负载交易



```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf createrawtransaction "[{\"txid\":\"5edeaf9f9a628bbfb00c08bba62f4ec8e1f3c87f8ee96261a80668e44413bec3\",\"vout\":0}]" "{}"

0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff0000000000
```



### 1.3.创建USDT交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createpayload_simplesend 2 0.20190625

000000000000000200000000013415a1
```



### 1.4.将USDT交易绑定到BTC交易上

```

omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createrawtx_opreturn 0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff0000000000 000000000000000200000000013415a1

0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff010000000000000000166a146f6d6e69000000000000000200000000013415a100000000


```

### 1.5.设置USDT的接收地址



```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createrawtx_reference 0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff010000000000000000166a146f6d6e69000000000000000200000000013415a100000000 muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe

0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff020000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000

```



### 1.6.设置找零地址以及BTC的手续费

omni_createrawtx_change

- rawtx：要扩展的裸交易，字符串，必需
- prevtxs：交易输入JSON数组，字符串，必需
- destination：找零目标，字符串，必需
- fee：期望的手续费，数值，必需
- position：找零输出位置(vout未知)，数值，可选，默认值：第一个



```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createrawtx_change 0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff020000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000 "[{\"txid\":\"5edeaf9f9a628bbfb00c08bba62f4ec8e1f3c87f8ee96261a80668e44413bec3\",\"vout\":0,\"scriptPubKey\":\"76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac\",\"value\":0.01000000}]" mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE 0.0002

0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff03fef10e00000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000
```



### 1.7.签名交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf signrawtransaction 0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e0000000000ffffffff03fef10e00000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000 "[{\"txid\":\"5edeaf9f9a628bbfb00c08bba62f4ec8e1f3c87f8ee96261a80668e44413bec3\",\"vout\":0,\"scriptPubKey\":\"76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac\",\"value\":0.01000000}]" [\"cQhGwrYFfPBrd5gRVkim9EsqKooTBWC8rSKjRuXemoayjXcSi52N\"]


0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e000000006a473044022077674c4e7575c22c6e772989b589a35d014ae1fe6b0329b7d7fbd3015b01e3da02203b0cc487766d2270c34370bf96b52b2b7cecceae01c0f6718ef779322ec860f8012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff03fef10e00000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000
```



### 1.8.解码原始交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf decoderawtransaction 0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e000000006a473044022077674c4e7575c22c6e772989b589a35d014ae1fe6b0329b7d7fbd3015b01e3da02203b0cc487766d2270c34370bf96b52b2b7cecceae01c0f6718ef779322ec860f8012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff03fef10e00000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000 

{
  "txid": "db0669c3c3c7e9d817387cbb31d5a51d7e31b7174a5f944d0eccd5d366e9e6c8",
  "hash": "db0669c3c3c7e9d817387cbb31d5a51d7e31b7174a5f944d0eccd5d366e9e6c8",
  "size": 256,
  "vsize": 256,
  "version": 1,
  "locktime": 0,
  "vin": [
    {
      "txid": "5edeaf9f9a628bbfb00c08bba62f4ec8e1f3c87f8ee96261a80668e44413bec3",
      "vout": 0,
      "scriptSig": {
        "asm": "3044022077674c4e7575c22c6e772989b589a35d014ae1fe6b0329b7d7fbd3015b01e3da02203b0cc487766d2270c34370bf96b52b2b7cecceae01c0f6718ef779322ec860f8[ALL] 02aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64dd",
        "hex": "473044022077674c4e7575c22c6e772989b589a35d014ae1fe6b0329b7d7fbd3015b01e3da02203b0cc487766d2270c34370bf96b52b2b7cecceae01c0f6718ef779322ec860f8012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64dd"
      },
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "value": 0.00979454,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 d2f9072629e2b14d5a246dfe583347ba140f45ea OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE"
        ]
      }
    }, 
    {
      "value": 0.00000000,
      "n": 1,
      "scriptPubKey": {
        "asm": "OP_RETURN 6f6d6e69000000000000000200000000013415a1",
        "hex": "6a146f6d6e69000000000000000200000000013415a1",
        "type": "nulldata"
      }
    }, 
    {
      "value": 0.00000546,
      "n": 2,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 983c8b990aef5747bdef1f2bf3a49d29b19ae157 OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe"
        ]
      }
    }
  ]
}
```






### 1.9.广播交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf sendrawtransaction  0100000001c3be1344e46806a86162e98e7fc8f3e1c84e2fa6bb080cb0bf8b629a9fafde5e000000006a473044022077674c4e7575c22c6e772989b589a35d014ae1fe6b0329b7d7fbd3015b01e3da02203b0cc487766d2270c34370bf96b52b2b7cecceae01c0f6718ef779322ec860f8012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff03fef10e00000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000013415a122020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000

db0669c3c3c7e9d817387cbb31d5a51d7e31b7174a5f944d0eccd5d366e9e6c8

```

### 1.10.查看交易详情

```
omnicore-cli  -conf=/root/.bitcoin/bitcoin-test.conf omni_gettransaction db0669c3c3c7e9d817387cbb31d5a51d7e31b7174a5f944d0eccd5d366e9e6c8

{
    "txid": "db0669c3c3c7e9d817387cbb31d5a51d7e31b7174a5f944d0eccd5d366e9e6c8",
    "fee": "0.00020000",
    "sendingaddress": "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE",
    "referenceaddress": "muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe",
    "ismine": true,
    "version": 0,
    "type_int": 0,
    "type": "Simple Send",
    "propertyid": 2,
    "divisible": true,
    "amount": "0.20190625",
    "valid": true,
    "blockhash": "00000000000003433e9bd50486bb7a8fb8589f3d442dc50a1587bb386a5dbd8a",
    "blocktime": 1561442205,
    "positioninblock": 1,
    "block": 1564956,
    "confirmations": 2
}





```

## 2.使用其他BTC地址支付手续费



### 2.1.真实的交易(某个案例)

以下是某个交易所真实的提币交易信息

```

txid: 7731cfa868255fda5b701a700baadf61bc4c725d5fbe83fa11137804e9ed54a8


omnicore-cli  -conf=/root/.bitcoin/bitcoin.conf getrawtransaction 7731cfa868255fda5b701a700baadf61bc4c725d5fbe83fa11137804e9ed54a8 1

{
  "hex": "0100000002735b3130c32dc40561a5a3b17f98162a311a8fce9771f9d2b6a8b7951230451d010000006b483045022100df0427c7958cf8519df39b9e664d2060ec899a5acc5b49937544a64d5c4a29cd02205d46139ddf72eb5bc64864e4eb60933863eec6b95e00496a3c29453b4f25f0a60121037699d6b3e704af16322cf2cbd1e614dc29e57ac071100ba96ca55475cecabdd0fffffffff086a602a5e3d0f106e79fb336cbe525d2deb1019eb9408d889cae55415fa502000000006b483045022100ac8e17a30167df9082606e2079a05cbeee2b7f3879c1a9425cf44527e47aaaa202206e99db535e22516a81c9207c311bc35569e12bf7544ae3dddf9d40f4f4b125650121030651e1d15ae9a284ffd712885529d3344db3700be756e6c22c56a6c1b57d359dffffffff034e130c00000000001976a914b64513c1f1b889a556463243cca9c26ee626b9a088ac22020000000000001976a914b64513c1f1b889a556463243cca9c26ee626b9a088ac0000000000000000166a146f6d6e69000000000000001f00000091815f5aa300000000",
  "txid": "7731cfa868255fda5b701a700baadf61bc4c725d5fbe83fa11137804e9ed54a8",
  "hash": "7731cfa868255fda5b701a700baadf61bc4c725d5fbe83fa11137804e9ed54a8",
  "size": 405,
  "vsize": 405,
  "version": 1,
  "locktime": 0,
  "vin": [
    {
      "txid": "1d45301295b7a8b6d2f97197ce8f1a312a16987fb1a3a56105c42dc330315b73",
      "vout": 1,
      "scriptSig": {
        "asm": "3045022100df0427c7958cf8519df39b9e664d2060ec899a5acc5b49937544a64d5c4a29cd02205d46139ddf72eb5bc64864e4eb60933863eec6b95e00496a3c29453b4f25f0a6[ALL] 037699d6b3e704af16322cf2cbd1e614dc29e57ac071100ba96ca55475cecabdd0",
        "hex": "483045022100df0427c7958cf8519df39b9e664d2060ec899a5acc5b49937544a64d5c4a29cd02205d46139ddf72eb5bc64864e4eb60933863eec6b95e00496a3c29453b4f25f0a60121037699d6b3e704af16322cf2cbd1e614dc29e57ac071100ba96ca55475cecabdd0"
      },
      "sequence": 4294967295
    }, 
    {
      "txid": "02a55f4155ae9c888d40b99e01b1ded225e5cb36b39fe706f1d0e3a502a686f0",
      "vout": 0,
      "scriptSig": {
        "asm": "3045022100ac8e17a30167df9082606e2079a05cbeee2b7f3879c1a9425cf44527e47aaaa202206e99db535e22516a81c9207c311bc35569e12bf7544ae3dddf9d40f4f4b12565[ALL] 030651e1d15ae9a284ffd712885529d3344db3700be756e6c22c56a6c1b57d359d",
        "hex": "483045022100ac8e17a30167df9082606e2079a05cbeee2b7f3879c1a9425cf44527e47aaaa202206e99db535e22516a81c9207c311bc35569e12bf7544ae3dddf9d40f4f4b125650121030651e1d15ae9a284ffd712885529d3344db3700be756e6c22c56a6c1b57d359d"
      },
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "value": 0.00791374,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 b64513c1f1b889a556463243cca9c26ee626b9a0 OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914b64513c1f1b889a556463243cca9c26ee626b9a088ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "1HckjUpRGcrrRAtFaaCAUaGjsPx9oYmLaZ"
        ]
      }
    }, 
    {
      "value": 0.00000546,
      "n": 1,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 b64513c1f1b889a556463243cca9c26ee626b9a0 OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914b64513c1f1b889a556463243cca9c26ee626b9a088ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "1HckjUpRGcrrRAtFaaCAUaGjsPx9oYmLaZ"
        ]
      }
    }, 
    {
      "value": 0.00000000,
      "n": 2,
      "scriptPubKey": {
        "asm": "OP_RETURN 6f6d6e69000000000000001f00000091815f5aa3",
        "hex": "6a146f6d6e69000000000000001f00000091815f5aa3",
        "type": "nulldata"
      }
    }
  ],
  "blockhash": "00000000000000000002e9ca95ed03e4134ca8b9c6056759249371a7767a6286",
  "confirmations": 178,
  "time": 1561365214,
  "blocktime": 1561365214
}


```





### 2.2.列出UTXO



```
omnicore-cli  -conf=/root/.bitcoin/bitcoin-test.conf listunspent  0 99999 [\"mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE\"]

{
    "txid": "2170db7b2c9fc4ac4ce33de6e0fb734b6d6fba3e27367fbc62f944a9868c943d",
    "vout": 2,
    "address": "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE",
    "account": "pluto",
    "scriptPubKey": "76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac",
    "amount": 0.00000546,
    "confirmations": 76287,
    "spendable": true,
    "solvable": true
 }

```



### 2.3.用于支付手续费的地址信息

```

mrYbVednwaU2rFbnCijWAL8iFHVc7LRwsx

cPtP7cYUvvmEF9KaSe52SuE5E8L2Sd6zbz3gJXHWWoBjCEEo2G9G
```



```
查询utxo


omnicore-cli  -conf=/root/.bitcoin/bitcoin-test.conf listunspent  0 99999 [\"mrYbVednwaU2rFbnCijWAL8iFHVc7LRwsx\"]

{
    "txid": "d86c6917f42b3faeee01af87563a2fe8512d4bb085c8be220cb4871f31cdce25",
    "vout": 1,
    "address": "mrYbVednwaU2rFbnCijWAL8iFHVc7LRwsx",
    "account": "user",
    "scriptPubKey": "76a91478f8da3e8fc8864711c915bcd5a577fb0f735cfa88ac",
    "amount": 0.00010700,
    "confirmations": 46665,
    "spendable": false,
    "solvable": false
  }


```







### 2.4.创建负载交易(注意区别!!)

 **必须把支付USDT的地址的UTXO要放在第0个**

```

omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf createrawtransaction "[{\"txid\":\"2170db7b2c9fc4ac4ce33de6e0fb734b6d6fba3e27367fbc62f944a9868c943d\",\"vout\":2},{\"txid\":\"d86c6917f42b3faeee01af87563a2fe8512d4bb085c8be220cb4871f31cdce25\",\"vout\":1}]" "{}"

01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff0000000000

```



### 2.5.查询支付USDT的地址的USDT测试币的余额

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf  omni_getbalance mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE 2
```



### 2.6.创建USDT交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createpayload_simplesend 2 0.06252047

000000000000000200000000005f660f
```


### 2.7.将USDT交易绑定到BTC交易上(插入OP_RETURN)

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createrawtx_opreturn 01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff0000000000 000000000000000200000000005f660f

01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff010000000000000000166a146f6d6e69000000000000000200000000005f660f00000000
```

### 2.8.添加USDT接收地址

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createrawtx_reference 01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff010000000000000000166a146f6d6e69000000000000000200000000005f660f00000000 muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe

01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff020000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000

```





### 2.9.添加找零地址(支付手续费的地址)

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf omni_createrawtx_change 01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff020000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000 "[{\"txid\":\"2170db7b2c9fc4ac4ce33de6e0fb734b6d6fba3e27367fbc62f944a9868c943d\",\"vout\":2,\"scriptPubKey\":\"76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac\",\"value\":0.00000546}, {\"txid\":\"d86c6917f42b3faeee01af87563a2fe8512d4bb085c8be220cb4871f31cdce25\",\"vout\":1,\"scriptPubKey\":\"76a91478f8da3e8fc8864711c915bcd5a577fb0f735cfa88ac\",\"value\":0.00010700}]" mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE 0.00002 0


01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff03fc210000000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000

```



### 2.10.签名交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf signrawtransaction 01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb70210200000000ffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd80100000000ffffffff03fc210000000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000 "[{\"txid\":\"2170db7b2c9fc4ac4ce33de6e0fb734b6d6fba3e27367fbc62f944a9868c943d\",\"vout\":2,\"scriptPubKey\":\"76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac\",\"value\":0.00000546},{\"txid\":\"d86c6917f42b3faeee01af87563a2fe8512d4bb085c8be220cb4871f31cdce25\",\"vout\":1,\"scriptPubKey\":\"76a91478f8da3e8fc8864711c915bcd5a577fb0f735cfa88ac\",\"value\":0.00010700}]" [\"cQhGwrYFfPBrd5gRVkim9EsqKooTBWC8rSKjRuXemoayjXcSi52N\",\"cPtP7cYUvvmEF9KaSe52SuE5E8L2Sd6zbz3gJXHWWoBjCEEo2G9G\"]

{
  "hex": "01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb7021020000006a47304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd8010000006b483045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a012103457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0ffffffff03fc210000000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000",
  "complete": true
}
```

> 注意: 私钥数组中的 ','两边不能有空格, 否则会报错: error: Error parsing JSON:["cQhGwrYFfPBrd5gRVkim9EsqKooTBWC8rSKjRuXemoayjXcSi52N",


### 2.11.解码交易


```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf decoderawtransaction 01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb7021020000006a47304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd8010000006b483045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a012103457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0ffffffff03fc210000000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000


{
  "txid": "f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721",
  "hash": "f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721",
  "size": 404,
  "vsize": 404,
  "version": 1,
  "locktime": 0,
  "vin": [
    {
      "txid": "2170db7b2c9fc4ac4ce33de6e0fb734b6d6fba3e27367fbc62f944a9868c943d",
      "vout": 2,
      "scriptSig": {
        "asm": "304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a[ALL] 02aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64dd",
        "hex": "47304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64dd"
      },
      "sequence": 4294967295
    }, 
    {
      "txid": "d86c6917f42b3faeee01af87563a2fe8512d4bb085c8be220cb4871f31cdce25",
      "vout": 1,
      "scriptSig": {
        "asm": "3045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a[ALL] 03457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0",
        "hex": "483045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a012103457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0"
      },
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "value": 0.00008700,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 d2f9072629e2b14d5a246dfe583347ba140f45ea OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE"
        ]
      }
    }, 
    {
      "value": 0.00000000,
      "n": 1,
      "scriptPubKey": {
        "asm": "OP_RETURN 6f6d6e69000000000000000200000000005f660f",
        "hex": "6a146f6d6e69000000000000000200000000005f660f",
        "type": "nulldata"
      }
    }, 
    {
      "value": 0.00000546,
      "n": 2,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 983c8b990aef5747bdef1f2bf3a49d29b19ae157 OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe"
        ]
      }
    }
  ]
}



```

### 2.11.广播交易

```
omnicore-cli -conf=/root/.bitcoin/bitcoin-test.conf sendrawtransaction  01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb7021020000006a47304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd8010000006b483045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a012103457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0ffffffff03fc210000000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000 

f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721


```



### 2.12.查看交易详情



```

omnicore-cli  -conf=/root/.bitcoin/bitcoin-test.conf  omni_gettransaction f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721 
{
  "txid": "f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721",
  "fee": "0.00002000",
  "sendingaddress": "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE",
  "referenceaddress": "muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe",
  "ismine": true,
  "version": 0,
  "type_int": 0,
  "type": "Simple Send",
  "propertyid": 2,
  "divisible": true,
  "amount": "0.06252047",
  "confirmations": 0
}


```

### 2.13.查看裸交易

```

omnicore-cli  -conf=/root/.bitcoin/bitcoin-test.conf  getrawtransaction f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721 1

{
  "hex": "01000000023d948c86a944f962bc7f36273eba6f6d4b73fbe0e63de34cacc49f2c7bdb7021020000006a47304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64ddffffffff25cecd311f87b40c22bec885b04b2d51e82f3a5687af01eeae3f2bf417696cd8010000006b483045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a012103457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0ffffffff03fc210000000000001976a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac0000000000000000166a146f6d6e69000000000000000200000000005f660f22020000000000001976a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac00000000",
  "txid": "f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721",
  "hash": "f30937d9b8f13c2ec5d4ef4343a1e09ed316eb83ac9cc3ff17a939fea9357721",
  "size": 404,
  "vsize": 404,
  "version": 1,
  "locktime": 0,
  "vin": [
    {
      "txid": "2170db7b2c9fc4ac4ce33de6e0fb734b6d6fba3e27367fbc62f944a9868c943d",
      "vout": 2,
      "scriptSig": {
        "asm": "304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a[ALL] 02aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64dd",
        "hex": "47304402202354f943053ff744672afe738951ed22e7ce0b2313127464eb96a3f8bff757000220678efd51f10adc5de23cc94bae4662d4a1afe519285062da704a09bd5c2c4c4a012102aec8e91921c8296ff5e8ff6c6666cd3090b78f3552939ad396079beb478b64dd"
      },
      "sequence": 4294967295
    }, 
    {
      "txid": "d86c6917f42b3faeee01af87563a2fe8512d4bb085c8be220cb4871f31cdce25",
      "vout": 1,
      "scriptSig": {
        "asm": "3045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a[ALL] 03457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0",
        "hex": "483045022100a769e75987326bc8e9bfdc7d4e8ec17cea9338ed73909593eeb0d3bb07aaf0a402205c3c02d5c1f98f92adf0e7e76ba6591438f9d865c3c1fff4f9bd7c8f7a47423a012103457e7713c9fa5eb7a6ce22371ff7be92bc51edf610a8eaa275c19b1a77821da0"
      },
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "value": 0.00008700,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 d2f9072629e2b14d5a246dfe583347ba140f45ea OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914d2f9072629e2b14d5a246dfe583347ba140f45ea88ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "mzkUX6sZ3bSqK7wk8sZmrR7wUwY3QJQVaE"
        ]
      }
    }, 
    {
      "value": 0.00000000,
      "n": 1,
      "scriptPubKey": {
        "asm": "OP_RETURN 6f6d6e69000000000000000200000000005f660f",
        "hex": "6a146f6d6e69000000000000000200000000005f660f",
        "type": "nulldata"
      }
    }, 
    {
      "value": 0.00000546,
      "n": 2,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 983c8b990aef5747bdef1f2bf3a49d29b19ae157 OP_EQUALVERIFY OP_CHECKSIG",
        "hex": "76a914983c8b990aef5747bdef1f2bf3a49d29b19ae15788ac",
        "reqSigs": 1,
        "type": "pubkeyhash",
        "addresses": [
          "muPuXyRqLBRf8Xyj28d2As8ya4iaw8XWGe"
        ]
      }
    }
  ],
  "blockhash": "000000004715a9959c19e08cd6ac8bc59e03d4e0161498c5cfdbd12ab0abbbda",
  "confirmations": 1,
  "time": 1561468755,
  "blocktime": 1561468755
}


```





## 3.总结

- 使用其他BTC地址支付手续费, 需要注意的是, 在创建负载交易的时候输入的UTXO顺序, 支付USDT的地址的UTXO必须放在第0个, 其他步骤和简单裸交易创建无异




## 4.参考

- <https://github.com/OmniLayer/omnicore/wiki/Use-the-raw-transaction-API-to-create-a-Simple-Send-transaction>

- 获取USDT测试币:  moneyqMan7uh8FqdCA2BV5yZ8qVrc9ikLP
- 获取BTC测试币:   https://coinfaucet.eu/en/btc-testnet/
- BTC测试链区块链浏览器和水龙头: [https://tbtc.bitaps.com](https://tbtc.bitaps.com/)

