const ganache = require('ganache-cli');
const {interface, bytecode} = require('../compile');
const Web3 = require('web3');
const web3 = new Web3(ganache.provider());


deploy = async ()=>{
    const accounts =  await web3.eth.getAccounts();
    console.log(accounts[0]);
    const result = await new web3.eth.Contract(JSON.parse(interface))
        .deploy({data:'0x'+bytecode})  //注意: 需要 加 '0x', 否则报错
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