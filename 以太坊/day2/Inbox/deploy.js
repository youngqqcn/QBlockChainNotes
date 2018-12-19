const {interface, bytecode} = require('./compile');
const Web3 = require('web3');
const HDWalletProvider = require('truffle-hdwallet-provider');

//注册以太坊账号时, 获取的助记词
const mnemonic = "mother citizen apart father resemble coral section pony floor brother fuel lottery";

//在infura注册账号,并创建项目, 设置Rinkeby网络,即可获取链接
const provider = new HDWalletProvider(mnemonic, "https://rinkeby.infura.io/v3/db5a95cd5605439b8983f00bc6433878"); 
const web3 = new Web3(provider);


deploy = async ()=>{
    const accounts =  await web3.eth.getAccounts();
    console.log(accounts[0]);
    const result = await new web3.eth.Contract(JSON.parse(interface))
        .deploy({data:'0x'+bytecode, arguments:['abc']})  //注意: 需要 加 '0x', 否则报错 
        .send({from:accounts[0], gas:'3000000'}); //gas limit 

    console.log("地址" + result.options.address);

    let message = await result.methods.getMessage().call();
    console.log(message);

    //测试setMessage
    await result.methods.setMessage("i am yqq").send({
        from : accounts[0],
        gas : '3000000',
    });

    message = await result.methods.getMessage().call();
    console.log(message);

};

deploy();