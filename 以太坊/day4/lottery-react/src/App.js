import React, { Component } from 'react';
// import logo from './logo.svg';
// import './App.css';
// import 'semantic-ui-css/semantic.min.css'
import {Message, Container,Button,Statistic, Card, Icon,Image, Label, Text} from 'semantic-ui-react'
// import { Text, View } from 'react-native'
import web3 from './web3';
import lottery from './lottery';

class App extends Component {

    // constructor(pros){
    //     super(pros);
    //     this.state = {manager:''};
    // }
    state = {
        manager:'',
        playersCount : '0',
        balance : '0',
        loading:false,
        pickLoading:false,
        showButton : 'none',
    };

    async componentDidMount(){
        const managerAddress = await lottery.methods.getManager().call();
        const playersCount = (await lottery.methods.getPlayersCount().call()).toString();
        const balance = web3.utils.fromWei( (await lottery.methods.getBalance().call()), 'ether').toString();
        this.setState({manager:managerAddress, playersCount:playersCount, balance:balance, loading:false});


        let accounts = await web3.eth.getAccounts();
        if(accounts.length > 0){
            if(accounts[0] === managerAddress){
                this.setState({showButton:'inline'});
            }else {
                this.setState({showButton:'none'});
            }
        }else{
            this.setState({showButton:'none'});
        }



    }


    enter = async ()=>{
        console.log("点击了");
        this.setState({loading:true});
        let accounts = await web3.eth.getAccounts();
        await lottery.methods.enter().send({
            from:accounts[0],
            value:web3.utils.toWei('1', 'ether'),
        });

        this.setState({loading:false});

        window.location.reload(true);

    };


    pickWinner = async ()=>{

        this.setState({pickLoading:true});

        let accounts = await web3.eth.getAccounts();

        await lottery.methods.pickWinner().send({
            from:accounts[0],
        });


        this.setState({pickLoading:false});
        window.location.reload(true);
    };




    render() {
        console.log(web3.version);
        // console.log(lottery.methods.getManager().call({}));
        
        
        return (
            <div >
                <br></br>

                <Container>
                    <Message info>
                        <Message.Header>我的彩票项目</Message.Header>
                        <p>hello</p>

                    </Message>

                    <Card.Group>
                        <Card>
                            <Image src='/images/log.png' />
                            <Card.Content>
                                <Card.Header>Q彩</Card.Header>
                                <Card.Meta>
                                    <p>管理员:</p>
                                    <Label size='mini' horizontal='true' >
                                        {this.state.manager}
                                    </Label>
                                </Card.Meta>
                                <Card.Description>每天20:00开奖</Card.Description>
                            </Card.Content>
                            <Card.Content extra>
                                <a>
                                    <Icon name='user' />
                                    {this.state.playersCount}参与
                                </a>
                            </Card.Content>
                            <Card.Content extra>
                                <Statistic color='red'>
                                    <Statistic.Value>{this.state.balance} ether</Statistic.Value>
                                </Statistic>
                            </Card.Content>

                                <Button animated='fade' color='red' onClick={this.enter} loading={this.state.loading} disabled={this.state.loading} >
                                    <Button.Content visible >一夜暴富从这里开始</Button.Content>
                                    <Button.Content hidden>投注1块钱,立即参与</Button.Content>
                                </Button>
                                <Button color='black' style={{display:this.state.showButton}}  >退 钱</Button>
                                <Button color='orange' style={{display: this.state.showButton}} onClick={this.pickWinner} loading={this.state.pickLoading} disabled={this.state.pickLoading}   >开 奖</Button>
                        </Card>

                    </Card.Group>

                </Container>

            </div>
        );
    }
}

export default App;
