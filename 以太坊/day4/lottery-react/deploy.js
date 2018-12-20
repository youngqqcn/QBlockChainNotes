const HDWalletProvider = require('truffle-hdwallet-provider');
const mnemonic = "mother citizen apart father resemble coral section pony floor brother fuel lottery";
const provider = new HDWalletProvider(mnemonic, "https://rinkeby.infura.io/v3/db5a95cd5605439b8983f00bc6433878");
const Web3 = require('web3');
const web3 = new Web3(provider);
const {interface, bytecode} = require('./compile');


deploy = async ()=>{
    const accounts =  await web3.eth.getAccounts();
    console.log("账户: "+ accounts[0]);
    const result = await new web3.eth.Contract(JSON.parse(interface))
        .deploy({data:'0x'+bytecode})  //注意: 需要 加 '0x', 否则报错
        .send({from:accounts[0], gas:'3000000'}); //gas limit 

    console.log("合约地址:" + result.options.address);


    console.log("------------------");
    console.log(interface);

};

deploy();