# Bitcoin 通用API服务



## exlectrs:

- API后台服务(Rust语言编写) https://github.com/Blockstream/electrs.git

- 使用electr作为后台的区块链浏览器:https://github.com/Blockstream/esplora.git



https://github.com/Blockstream/electrs

https://github.com/romanz/electrs/blob/master/doc/usage.md







##　btcapiserver

- https://github.com/bitaps-com/btcapiserver.git
- https://github.com/bitaps-com/pybtc
- https://github.com/bitaps-com/aiojsonrpc



## bitcores

 https://github.com/bitpay/bitcore/



部署步骤:

- 服务器配置: 8 核, 16G,   1TB+  SSD

- 比特币全节点(或者可靠的peer节点)

- 安装mongodb  3.4 及以上

  修改 `/etc/mongo.conf` , 设置数据存储路径, 将SSD挂在到 对应的路径下

  ```
  storage:
     dbPath: /data1/mongo
     journal:
       enabled: true
  
  net:
     port: 27017
     bindIp: 0.0.0.0 
  ```

  

- gcc 和 g++

- CentOS 7
- node: v10.21.0
- bitcore version: master (commit: 734107b)

```
git clone https://github.com/bitpay/bitcore.git

npm cache clean --force
rm -rf node_modules
rm -rf package-lock.json

#使用 cnpm 替换 npm

npm config set registry https://registry.npm.taobao.org

npm install -g cnpm --registry=https://registry.npm.taobao.org

cnpm install 


#如果报警告: eslint@^4.9.0 is not installed , 安装一下  eslint@4.9.0

cnpm install cnpm install eslint@4.9.0


然后运行

cnpm  run node 



#可以启动浏览器
NETWORK=mainnet CHAIN=BTC cnpm run insight
```









Bitcoin相关库

Python

- https://github.com/richardkiss/pycoin
- https://github.com/petertodd/python-bitcoinlib
- https://github.com/chainside/btcpy
- https://github.com/1200wd/bitcoinlib.git