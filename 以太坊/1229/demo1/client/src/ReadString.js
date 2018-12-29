//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-29 12:36
 * @descriptions:
 *
 * //https://truffleframework.com/tutorials/getting-started-with-drizzle-and-react#quick-recap
 * 笔记:
 * 最重要的是: 通过Drizzle获取智能合约中变量的值
 *   第1步: 告诉Drizzle你要监视那个变量, Drizzle返回给你一个dataKey, 这个dataKey后面会用到;
 *   第2步: 由于Drizzle是异步的, 你应该注意drizzleState的变化.
 *          一旦变量存在, 就可以通过dataKey获取你想要的变量的值了
 *
 *
 */


import React from "react";

class ReadString extends React.Component {
    state = { dataKey: null };

    componentDidMount() {
        const { drizzle } = this.props;
        //获取智能合约
        const contract = drizzle.contracts.MyStringStore;

        // let drizzle know we want to watch the `myString` method
        //跟踪myString变量的getter()方法
        const dataKey = contract.methods["myString"].cacheCall();

        // save the `dataKey` to local component state for later reference
        this.setState({ dataKey });
    }

    render() {
        // get the contract state from drizzleState
        const { MyStringStore } = this.props.drizzleState.contracts;

        // using the saved `dataKey`, get the variable we're interested in
        const myString = MyStringStore.myString[this.state.dataKey];

        // if it exists, then we display its value
        return <p>My stored string: {myString && myString.value}</p>;
    }
}


export default ReadString;