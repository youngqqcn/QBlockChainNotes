//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-19 11:42
 * @descriptions:
 */
//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-19 11:24
 * @descriptions:
 */


const HDWalletProvider = require('truffle-hdwallet-provider');
const mnemonic = "mother citizen apart father resemble coral section pony floor brother fuel lottery";
const provider = new HDWalletProvider(mnemonic, "https://rinkeby.infura.io/v3/db5a95cd5605439b8983f00bc6433878");
const Web3 = require('web3');
const web3 = new Web3(provider);

// const ganache = require('ganache-cli');
// const web3 = new Web3(ganache.provider());



send = async ()=>{

    const accounts = ['0x954d1a58c7abd4ac8ebe05f59191Cf718eb0cB89', '0xc6a6FdBcab9eA255eDEE2e658E330a62f793B74E'];
    let accout0Balance = await web3.eth.getBalance(accounts[0]);
    let accout1Balance = await web3.eth.getBalance(accounts[1]);

    console.log('account[0] = '+ accout0Balance + ' wei');
    console.log('account[1] = '+ accout1Balance + ' wei');



    let strData  = '穆里尼奥离开了曼联';
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

};


send();






