//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-19 12:30
 * @descriptions:
 */

const HDWalletProvider = require('truffle-hdwallet-provider');
const mnemonic = "mother citizen apart father resemble coral section pony floor brother fuel lottery";
const provider = new HDWalletProvider(mnemonic, "https://rinkeby.infura.io/v3/db5a95cd5605439b8983f00bc6433878");
const Web3 = require('web3');
const web3 = new Web3(provider);

const express = require('express');  //使用express作为web框架
const app = express();

app.get('/send/:address', async (req, res) => {
    let toAddress = req.params.address;
    console.log(toAddress);

    const accounts = ['0x954d1a58c7abd4ac8ebe05f59191Cf718eb0cB89', toAddress];
    let accout0Balance = await web3.eth.getBalance(accounts[0]);
    let accout1Balance = await web3.eth.getBalance(accounts[1]);

    console.log('account[0] = '+ accout0Balance + ' wei');
    console.log('account[1] = '+ accout1Balance + ' wei');


    let strData  = '真他妈的什么人都有!'; //设置转账备注
    let inputData = '0x' + Buffer.from(strData).toString('hex');


    await web3.eth.sendTransaction({
        from:accounts[0],
        to: accounts[1],
        value: web3.utils.toWei('1', 'ether'),
        data:inputData
    });

    accout0Balance = await web3.eth.getBalance(accounts[0]);
    accout1Balance = await web3.eth.getBalance(accounts[1]);

    console.log('account[0] = '+ accout0Balance + ' wei');
    console.log('account[1] = '+ accout1Balance + ' wei');


    res.send("转账成功");
     //res.send(req.params.address);
});


app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.listen(3000, () => {
   console.log('Example app listening on port 3000!');
});
