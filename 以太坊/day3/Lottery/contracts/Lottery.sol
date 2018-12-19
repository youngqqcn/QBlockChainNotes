pragma solidity ^0.4.17 ;

/*
author:yqq
data:2018-12-19  18:12
desc: 彩票
*/


contract Lottery{

    address public manager; //管理员
    address[] public players;


    function Lottery() public{
        manager = msg.sender;//管理员
    }

    function getManager()view public returns(address){
        return manager;
    }

    //投注彩票
    function enter() public payable{
        require(msg.value == 1 ether);
        players.push(msg.sender);
    }

    //返回所有投彩人
    function getAllPlayers() public view returns(address[]){
        return players;
    }

    //获取奖池金额
    function getBalance() view public returns(uint){
        return this.balance;
    }

    //获取彩民数量
    function getPlayersCount() public view returns(uint){
        return players.length;
    }


    function random() private returns(uint){
        //区块时间
        //block.difficulty
        //now
        //players

        return uint(keccak256(block.difficulty, now, players));
    }



    //开奖
    function pickWinner() public onlyManager returns(address){

        //require(msg.sender == manager);

        uint winnerIndex = random() % getPlayersCount();
        address winner = players[winnerIndex];

        winner.transfer(this.balance);
        delete players;

        return winner;
    }

    //退款
    function refund() public onlyManager {
        //require(msg.sender == manager);
        for(uint i = 0; i < players.length; i++){
            players[i].transfer(1 ether);
        }
        delete players;
    }

    modifier onlyManager(){
        require(msg.sender == manager);
        _;  //表示要执行代码
    }

}
