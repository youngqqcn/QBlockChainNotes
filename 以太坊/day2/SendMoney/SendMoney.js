//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-19 11:24
 * @descriptions:
 */




const Web3 = require('web3');
const ganache = require('ganache-cli');
const web3 = new Web3(ganache.provider());



send = async ()=>{

    const accounts = await web3.eth.getAccounts();
    let accout0Balance = await web3.eth.getBalance(accounts[0]);
    let accout1Balance = await web3.eth.getBalance(accounts[1]);

    console.log('account[0] = '+ accout0Balance + ' wei');
    console.log('account[1] = '+ accout1Balance + ' wei');


    await web3.eth.sendTransaction({
        from:accounts[0],
        to: accounts[1],
        value: web3.utils.toWei('15', 'ether')
    });

    accout0Balance = await web3.eth.getBalance(accounts[0]);
    accout1Balance = await web3.eth.getBalance(accounts[1]);

    console.log('account[0] = '+ accout0Balance + ' wei');
    console.log('account[1] = '+ accout1Balance + ' wei');


};


send();






