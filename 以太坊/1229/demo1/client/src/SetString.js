//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-29 13:07
 * @descriptions:
 */

import React from 'react';

class SetString extends  React.Component{

    state = {stackId:null};

    handleKeyDown = (e) =>{
        if (e.keyCode === 13){
            this.setValue(e.target.value);
        }
    } ;

    setValue = (value)=>{
        const {drizzle, drizzleState } = this.props;

        const contract = drizzle.contracts.MyStringStore;

        //调用set函数
        const stackId = contract.methods["set"].cacheSend(value, {from:drizzleState.accounts[1]})

        //保存stackId
        this.setState({stackId});
    };

    getTxStatus = ()=>{
        //从drizzlestate 获取 交易状态信息
        const {transactions, transactionStack} = this.props.drizzleState;

        //通过stackId获取交易hash
        const txHash  = transactionStack[this.state.stackId];

        if (!txHash) return null;

        return `Trasaction status: ${transactions[txHash].status}`
    };


    render(){
        return (
            <div>
                <input type="text" onKeyDown={this.handleKeyDown}/>
                <div>{this.getTxStatus()}</div>
            </div>

        );

    };

}

export default SetString;