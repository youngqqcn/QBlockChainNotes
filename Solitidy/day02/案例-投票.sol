/*
author:yqq
date:2018-12-17  14:07 
desc : solidiy notes
*/

pragma solidity ^0.4.21;
pragma experimental ABIEncoderV2;


contract VoteContract{
    
    struct Voter{
        uint voteNumber;
        bool isVoted;
        uint weight;
        address delegate; //agent
    }
    
    struct Candidate{
        string name;
        uint voteCount;
    }
    
    address public admin; 
    
    
    Candidate[] public candidates;
    mapping(address => Voter) public voters; 
    
    
	//创建候选人
    function VoteContract(string[] candidatesNames) public{
        admin = msg.sender; //设置管理员
        for(uint i = 0; i < candidatesNames.length; i++){
            Candidate memory tmp =  Candidate({name:candidatesNames[i], voteCount:0});
            candidates.push(tmp);
        }
    }
    
	//函数修饰器,  检查当前用户是否是管理员
    modifier AdminOnly() {
        require(admin == msg.sender);
        _ ;
    }
    
	//管理员 给其他投票人  赋予权限
    function giveVoteRightTo(address addr) AdminOnly public{
        if(voters[addr].weight > 0){
            revert();
        }
        voters[addr].weight = 1;
    }
    
	//投票
    function vote(uint voteNumber) public{
       // Voter memory voter = voters[msg.sender]; // error, 必须是引用,不能是值类型
        Voter storage voter = voters[msg.sender]; //
        if(voter.weight <= 0 || voter.isVoted){
            revert();
        }
        voter.isVoted = true;
        voter.voteNumber = voteNumber;
        candidates[voteNumber].voteCount += voter.weight;
    }
    
    //投票人设置代理人
    function delegateFunc(address to ) public{
        Voter storage voter = voters[msg.sender];
        if(voter.weight <= 0 || voter.isVoted){
            revert();
        }
        
        //如果指定的代理人, 指定了他人做代理, 那么要找到最终的代理人
        while(voters[to].delegate != address(0) && voters[to].delegate != msg.sender){
            to = voters[to].delegate;
        }
        
        //且最终代理人, 不能是自己
        require(msg.sender != to);
        
        voter.isVoted = true;
        voter.delegate = to;
        
        Voter finalDelegateVoter = voters[to];
        if(finalDelegateVoter.isVoted == true){ 
            //判断代理人是否已经投票, 如果已经投票, 直接投票给代理人投的那个人
            candidates[finalDelegateVoter.voteNumber].voteCount += voter.weight;
        }else{
            //如果代理人没有通过票, 则将代理人的权重加上自己的权重
            finalDelegateVoter.weight += voter.weight; 
        }
    }
    
    
    //查询投票结果
    function whoWin() public returns(string, uint){
        string winnerName;
        uint winnerVoteCount = 0;
        for (uint i = 0; i < candidates.length; i++){
            if(winnerVoteCount < candidates[i].voteCount){
                winnerVoteCount = candidates[i].voteCount;
                winnerName = candidates[i].name;
            }
        }
        return (winnerName, winnerVoteCount);
    }
    
    
}
