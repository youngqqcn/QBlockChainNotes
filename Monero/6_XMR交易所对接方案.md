# 交易所对接 XMR 



## 充币

### 用户充币地址生成

使用 subaddress 即可



### 充币数据监测

> monero-wallet-rpc 的API文档:   https://web.getmonero.org/resources/developer-guides/wallet-rpc.html



 **步骤1** :   使用  `monero-wallet-cli`  的以下选项生成 `incoming-only`钱包:

```
--generate-from-view-key arg   //Generate incoming-only wallet from view key
```



观察钱包生成过程

```
monero-wallet-cli --stagenet  --daemon-address monero-stagenet.exan.tech:38081  --trusted-daemon --generate-from-view-key=/root/.bitmonero/stagenet/wallet_files/yqq_incoming_only  --restore-height 536084  
```

  

![](./img/generate_incoming_only_wallet.png)





**步骤2**: 使用 `monero-wallet-rpc` 导入上一步生成的`Private View Key` 作为 `incoming-only` 钱包.   这样就可以RPC接口获取钱包的入账数据.

- 启动  monero-wallet-rpc  ,  注意端口不要学wiki页面中把端口设置为  `18082`(主网) 或 `38082`(测试网)(默认是ZMQ的RPC端口)

  ```
  monero-wallet-rpc --stagenet --daemon-address  monero-stagenet.exan.tech:38081 --trusted-daemon --wallet-file=/root/.bitmonero/stagenet/wallet_files/yqq_incoming_only --confirm-external-bind --rpc-bind-ip 0.0.0.0 --rpc-bind-port 38089  --password 123456 --disable-rpc-login --detach
  ```


![](./img/start_wallet_rpc_wtih_incoming_only_wallet.png)





- 优雅停止

  ```
  curl -X POST http://127.0.0.1:38089/json_rpc -d '{"jsonrpc":"2.0","id":"0","method":"stop_wallet"}' -H 'Content-Type: application/json' 
  ```



- **incoming_transfers**   获取钱包的所有入账交易信息,  (需要先调用  `auto_refresh` 让rpc进程自动扫描, 经过实践, 其实不调用也用 `auto_refresh`也可以, 有入账交易也会扫描到)

  Return a list of incoming transfers to the wallet.

  Inputs:

  - *transfer_type* - string; "all": all the transfers, "available": only transfers which are not yet spent, OR "unavailable": only transfers which are already spent.
  - *account_index* - unsigned int; (Optional) Return transfers for this account. (defaults to 0)
  - *subaddr_indices* - array of unsigned int; (Optional) Return transfers sent to these subaddresses.
  - *verbose* - boolean; (Optional) Enable verbose output, return key image if true.

  Outputs:

  - transfers\- list of:
    - *amount* - unsigned int; Amount of this transfer.
    - *global_index* - unsigned int; Mostly internal use, can be ignored by most users.
    - *key_image* - string; Key image for the incoming transfer's unspent output (empty unless verbose is true).
    - *spent* - boolean; Indicates if this transfer has been spent.
    - *subaddr_index* - unsigned int; Subaddress index for incoming transfer.
    - *tx_hash* - string; Several incoming transfers may share the same hash if they were in the same transaction.
    - *tx_size* - unsigned int; Size of transaction in bytes.



如果  result 为空   则为   `"result":{}`

```
[root@demo xmr]# curl -X POST https://192.168.10.160:38089/json_rpc -d '{"jsonrpc":"2.0","id":"0","method":"incoming_transfers","params":{"transfer_type":"all"}}' -H 'Content-Type: application/json' --insecure


{
  "id": "0",
  "jsonrpc": "2.0",
  "result": {
    "transfers": [{
      "amount": 10000000000000,
      "block_height": 536084,
      "frozen": false,
      "global_index": 2329106,
      "key_image": "0da9c81fee4bcf650f9a112811e551f8a6062a9fa3b8c9e4d70c568fa3505557",
      "spent": true,
      "subaddr_index": {
        "major": 0,
        "minor": 0
      },
      "tx_hash": "533cdbf4f258840d9178875637aabbd89ba0a273c2edad14eaaee7bd486d98d1",
      "unlocked": true
    },{
      "amount": 10000000000000,
      "block_height": 538496,
      "frozen": false,
      "global_index": 2359202,
      "key_image": "d0f89cd8c09e16d3a98659949ca7d4c1eca2da25e175fb8f2fae56334ab0b993",
      "spent": false,
      "subaddr_index": {
        "major": 0,
        "minor": 2
      },
      "tx_hash": "920ab12c72c89c5e8e527419ed401e99ce9373db26ccf82bd68caaeac299e312",
      "unlocked": true
    }]
  }
}
```



根据返回的数据, 并没有直接得到 subaddress, 只有  `major` 和 `minor`的信息,   有以下2种方式可以获得subaddress的地址字符串信息

- 根据**主地址**的 `Private View Key`和`Public Spend Key`(public spend key 可直接由master standard address得到)推导出  `( major, minor ) `的地址(推导过程可以看 [2_XMR的技术概念.md](2_XMR的技术概念.md) 和 [3_XMR地址生成.md](3_XMR地址生成.md))

- 根据  `get_address` RPC 接口可以通过   `major`和 `minor` 获取地址

  **get_address**

  Return the wallet's addresses for an account. Optionally filter for specific set of subaddresses.

  Alias: *getaddress*.

  Inputs:

  - *account_index* - unsigned int; Return subaddresses for this account.
  - *address_index* - array of unsigned int; (Optional) List of subaddresses to return from an account.

  Outputs:

  - *address* - string; The 95-character hex address string of the monero-wallet-rpc in session.

  - addresses

    array of addresses informations

    - *address* string; The 95-character hex (sub)address string.
    - *label* string; Label of the (sub)address
    - *address_index* unsigned int; index of the subaddress
    - *used* boolean; states if the (sub)address has already received funds

  ```
  [root@demo xmr]# curl -X POST http://127.0.0.1:38089/json_rpc -d '{"jsonrpc":"2.0","id":"0","method":"get_address","params":{"account_index":0,"address_index":[2]}}' -H 'Content-Type: application/json'
  
  
  {
    "id": "0",
    "jsonrpc": "2.0",
    "result": {
      "address": "56Trp8Gc9x5M5mLhxMqUaz5AuQpobGfHScyQKGMMmnZFcSFTj6zJFNDUGyDR5SVadjAmxgBp8qv1u2vZsEs8Vo1T4qqrFaa",
      "addresses": [{
        "address": "75kjb3c6SaM58L7fAWsB9UQfHhr1i2aRqLeH7rFDXJMkfm2XVAPw1EhVbtwcEgERCjGubTXADzUudBLm5f1Xg1r7AZXvwR5",
        "address_index": 2,
        "label": "",
        "used": true
      }]
    }
  }
  ```

  

## 提币

TODO







## 归集

使用`SubAddress` 不需要进行归集

