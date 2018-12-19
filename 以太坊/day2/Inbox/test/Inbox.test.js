//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-18 23:13
 * @descriptions:
 */

const assert = require('assert');
const ganache = require('ganache-cli');
const {interface, bytecode} = require('../compile');  //itface --> interface

//变量以大写开头, 表示是构造方法
const Web3 = require('web3');
const web3 = new Web3(ganache.provider());  //设置 ganache测试网络




describe('测试智能合约', ()=>{

    it('测试web3的版本', ()=>{
        console.log(web3.version);
    });
    
    
    it('测试web3的网络', ()=>{
        
        // console.log(web3.currentProvider);
        console.log(web3.utils.toHex("abcABC"));
        console.log(web3.utils.toHex({abc:"abc"}));
        console.log(web3.utils.fromAscii('ethereum', 32)); //将ascii码转为 十六进制字符串
        console.log(web3.utils.toWei('1', "ether")) //将以太币 转为  wei

    });


    it("测试web3的api", ()=>{
        web3.eth.getAccounts().then((accounts)=>{
            console.log(accounts);
        });
        web3.eth.getBalance('0x135D8ccF20f4125a547E2c8CaaEed04C422115EE').then((balance)=>{
            console.log(balance);
        });
    });

    it("使用ES6标准", async ()=>{
        const accounts =  await web3.eth.getAccounts();
        console.log(accounts);
        const money = await  web3.eth.getBalance(accounts[0]);
        console.log(web3.utils.fromWei(money, 'ether'), "eth");

    });


    it("测试部署智能合约", async ()=>{
        const accounts =  await web3.eth.getAccounts();
        const result = await new web3.eth.Contract(JSON.parse(interface))
            .deploy({data:bytecode, arguments:['abc']})
            .send({from:accounts[0], gas:1000000}); //gas limit 1000000刚刚,  太小会报错
        
        console.log("地址" + result.options.address);


        //测试getMessage
        let message = await result.methods.getMessage().call();
        console.log(message);
        assert.equal(message, "abc");


        //测试setMessage
        await result.methods.setMessage("i am yqq").send({
            from : accounts[0],
            gas : 1000000,
        });

        //再次读取
        message = await result.methods.getMessage().call();
        console.log(message);
        assert.equal(message, "i am yqq");

    });


});

