/*
author:yqq
date:2018-12-17  11:31
desc : solidiy notes
*/

pragma solidity ^0.4.20;

/*

 block blockhash(uint blockNumber)returns(bytes332),给定区块号的哈希值,只支持最近256个区块,且不
包含当前区块。
 block coinbaseaddress)当前块矿工的地址。
 blockdifficultyuint)当前块的难度。
 blockgaslimit(uint)当前块的gaslimit
 block number(uint)当前区块的块号。
 block timestamp(uint)当前块的时间戳。
msg.data(bytes)完整的调用数据(calldata)
msg.gas(uint)当前还剩的gas
msg.senderaddress)当前调用发起人的地址。
msg.sig(bytes4)调用数据的前四个字节(函数标识符)
msg.value(uint)这个消息所附带的货币量,单位为wei
now(uint)当前块的时间戳,等同于block.timestamp
tx. gasprice(uint)交易的gas价格。
tx.originaddress)交易的发送者(完整的调用链)
*/



 contract Test{
     bytes32 public blockhash;
     address public coinbase;
     uint public difficulty;
     uint public gaslimit;
     uint public blockNum;
     uint public timestamp;
     bytes public calldata;
     uint public gas;
     address public sender;
     bytes public sig;
     uint public msgvalue;
     uint public _now;
     uint public gasPrice;
     address public txOrigin;
     
     
     function tt() payable public {
         //给定区块号的哈希值,只支持最近256个区块,且不包含当前区块
         blockhash =block.blockhash(block.number-1);
         coinbase= block.coinbase;  //当前块矿工的地址。
         difficulty = block.difficulty; //当前块的难度。
         gaslimit = block.gaslimit;//uint);//当前块gaslimit的
         blockNum = block.number; //(uint)当前区块的块号
         timestamp=  block.timestamp; //(uint)当前块的时间戳
         calldata = msg.data;   
         gas=msg.gas;//(uint);//当前还剩的gas
         sender = msg.sender;//(address)当前调用发起人的地址。
         //sig=msg.sig; //(bytes4)调用数据的前四个字节(函数标识符)
        // msgValue = msg.value; //(uint)这个消息所附带的货币量,单位为wei
         _now=now;//(uint)当前块的时间戳,等同 Iblock于timestamp
         gasPrice = tx.gasprice;//(uint)交易的gas价格
         txOrigin = tx.origin;//(address);//交易的发送者(完整的调用链)
    }
}
