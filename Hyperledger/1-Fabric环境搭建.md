### Fabric环境搭建

> 我的系统: Ubuntu18.04, 假设你已经按照了docker-ce, docker-compose, nodejs , git,  curl, ....必要等工具. 如果没有,请按照"参考"一节中给出的文章链接安装相应工具.

- 配置docker阿里云加速器(后面需要下载大量文件)

  即将以下代码, 加入/etc/docker/docker.json中(如果没有则手动创建文件即可)

  ```
  {
  	"registry-mirrors": ["https://nawmuz9e.mirror.aliyuncs.com"]
  }
  ```

  > 可以参考: https://blog.csdn.net/michael_hm/article/details/79814159



- 下载引导脚本

  ```
  cd ~
  mkdir hyperledger
  cd hyperledger
  
  curl -sSL https://raw.githubusercontent.com/hyperledger/fabric/release-1.2/scripts/bootstrap.sh -o bootstrap.sh
  
  chmod 777 bootstrap.sh
  sudo ./bootstrap.sh 1.2.0 1.2.0 0.4.10
  ```

- 创建网络

  ```
  cd fabric-samples/first-network
  
  sudo ./byfn.sh -m generate
  
  sudo ../bin/cryptogen generate --config=./crypto-config.yaml      #生成初始区块
  
  export FABRIC_CFG_PATH=$PWD
  ```


- 生成初始区块

  ```
  sudo ../bin/cryptogen generate --config=./crypto-config.yaml
  
  export FABRIC_CFG_PATH=$PWD
  
  sudo ../bin/configtxgen -profile TwoOrgsOrdererGenesis -outputBlock ./channel-artifacts/genesis.block
  
  ```


- 生成应用通道的配置信息

  ```
  export CHANNEL_NAME=mychannel
  
  sudo ../bin/configtxgen -profile TwoOrgsChannel -outputCreateChannelTx ./channel-artifacts/channel.tx -channelID $CHANNEL_NAME
  
  ```


- 生成锚节点配置更新文件

  ```
  sudo ../bin/configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -channelID $CHANNEL_NAME -asOrg Org1MSP
  
  sudo ../bin/configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ./channel-artifacts/Org2MSPanchors.tx -channelID $CHANNEL_NAME -asOrg Org2MSP
  ```


- 操作网络

  ```
  sudo  docker-compose -f docker-compose-cli.yaml up -d
  ```

---



- 进入docker容器:

  ```
  docker exec  -it  cli bash
  ```


- 创建通道并加入通道

  ```
  export CHANNEL_NAME=mychannel
  
  peer channel create -o orderer.example.com:7050 -c $CHANNEL_NAME -f ./channel-artifacts/channel.tx --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
  
  peer channel join -b mychannel.block
  
  ```



----------------------------------------------



### 链码操作

- 安装链码

```
#代码在/opt/gopath/src/github.com目录下
peer chaincode install -n mycc -v 1.0 -p github.com/chaincode/chaincode_example02/go/     
```



- 实例化

```
peer chaincode instantiate -o orderer.example.com:7050 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C $CHANNEL_NAME -n mycc -v 1.0 -c '{"Args":["init","a", "100", "b","200"]}' -P "OR ('Org1MSP.peer','Org2MSP.peer')"
```



- 查询

```
#查询结果是100
peer chaincode query -C $CHANNEL_NAME -n mycc -c '{"Args":["query","a"]}'   
```



- 发起交易

```
#a给b转账 10
peer chaincode invoke -o orderer.example.com:7050  --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem  -C CHANNEL_NAME -n mycc -c '{"Args":["invoke","a","b","10"]}'      

#查询交易后账户余额, 正确结果是 90
peer chaincode query -C CHANNEL_NAME -n mycc -c '{"Args":["query","a"]}'   
```





### 运行fabcar项目

```
cd  fabric-samples/fabcar

docker rm -f $(docker ps -aq)

docker network prune -y

如果第一次运行:
使用 docker rmi  ?????   # 删除fabcar镜像

npm install    #安装nodejs依赖

--------------------------------------------

sudo ./startFabric.sh node  #启动

sudo node enrollAdmin.js    #注册管理员

sudo node registerUser.js   #注册user1

sudo node query.js   #查询

```



### 参考

>  https://www.jianshu.com/p/4f58e0fcb9f9

