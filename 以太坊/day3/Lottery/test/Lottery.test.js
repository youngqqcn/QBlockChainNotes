// 'use strict';

/**
 * @author: yqq
 * @create: 2018-12-19 18:14
 * @descriptions:
 */


const ganache = require('ganache-cli');
const Web3 = require('web3');
const web3  = new Web3(ganache.provider());
const assert = require('assert');
const {interface, bytecode} = require('../compile');


//去掉MaxListenersExceededWarning
require('events').EventEmitter.defaultMaxListeners = 15;


let gContract;
let accounts;
beforeEach(async ()=>{
    accounts =  await web3.eth.getAccounts();
    console.log(accounts[0]);
    gContract  = await new web3.eth.Contract(JSON.parse(interface))
        .deploy({data:'0x'+bytecode})  //注意: 需要 加 '0x', 否则报错
        .send({from:accounts[0], gas:'3000000'}); //gas limit

});



describe('测试区块链彩票', ()=>{


    it('测试智能合约的编译和部署', async ()=>{
        assert.ok(gContract.options.address);
    });


    it('测试智能合约彩票的投注', async ()=>{

        const beginMoney = await gContract.methods.getBalance().call();

        await gContract.methods.enter().send({
            from : accounts[1],
            gas : '3000000',
            value:  web3.utils.toWei('1', 'ether')
        });

        const endMoney = await gContract.methods.getBalance().call();

        // console.log("beginMoney=" + beginMoney);
        // console.log("endMoney =" + endMoney);

        assert.equal( web3.utils.toWei('1', 'ether'),  (endMoney - beginMoney));


    });


    it('测试智能合约彩票的投注  失败案例', async ()=>{

        let bSuccess = false;

        try {
            const beginMoney = await gContract.methods.getBalance().call();

            await gContract.methods.enter().send({
                from: accounts[1],
                gas: '3000000',
                value: web3.utils.toWei('1', 'ether')
            });

            const endMoney = await gContract.methods.getBalance().call();

            // console.log("beginMoney=" + beginMoney);
            // console.log("endMoney =" + endMoney);

            assert.equal(web3.utils.toWei('1', 'ether') - 10000, (endMoney - beginMoney));
            bSuccess = true;
        }catch (error) {
            bSuccess = false;
        }
        assert.equal(false, bSuccess);
    });



});








