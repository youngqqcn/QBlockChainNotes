pragma solidity ^0.4.17;


//用智能合约部署智能合约
contract FundingFactory{
    
    address[] public fundings; 
    
    function deploy(string _strProName, uint _nSupportMoney, uint _nGoalMoney) public{
        address funding = new Funding(_strProName, _nSupportMoney , _nGoalMoney, msg.sender);
        fundings.push(funding);
    }
    
}


contract Funding{
    
    bool bSuccessFlag = false;
    address public addrManager;
    string public strProjectName;
    uint public nSupportMoney;
    uint public nEndTime;
    uint public nGoalMoney;
    address []  public addrPlayers;
    mapping(address=>bool)  mapPlayer;  //使用mapping提高效率, 降低gas消耗
    
    
    PayRequest[]   public payRequests;  //付款请求结构体
    
    struct PayRequest{
        string  strDesc;
        uint    nPayment; //out 
        address addrShop;
        bool   bCompleted;
        mapping(address=>bool) mapVote;
        //address[] vctVotedAddr;
        uint  nAgreeCount; 
    }
    
    modifier onelyManager(){
        //require(bSuccessFlag);
        require(msg.sender == addrManager);
        _;
    }
    
    
    function   createRequest(string  _strDesc, uint _nPayment, address _addrShop) public onelyManager{
        PayRequest memory  payRequest =   PayRequest({
            strDesc : _strDesc,
            nPayment : _nPayment,
            addrShop : _addrShop,
            bCompleted : false,
            nAgreeCount : 0
        });
        
        payRequests.push(payRequest);
        
    }
    
    
    function Funding(string _strProName, uint _nSupportMoney, uint _nGoalMoney, address _manager) public{
        addrManager = _manager;//msg.sender;
        strProjectName = _strProName;
        nSupportMoney = _nSupportMoney;
        nGoalMoney = _nGoalMoney;
        nEndTime = now + 4 weeks;
       
    }
    
    function getBalance() view public returns(uint){
        return this.balance;
    }
    
    
    function getPlayersCount()public view returns(uint){
        return addrPlayers.length;
    }
    
    function getPlayers() public view returns(address[]){
        return addrPlayers;
    }
    
    function getRemainSeconds() public view returns(uint){
        return (nEndTime - now) ; //seconds
    }
    
    
    function checkStatus() view public{
        require(bSuccessFlag == false);
        require(now > nEndTime);
        require(this.balance > nGoalMoney);
    }
    
    function support() payable public{
        require(msg.value >= 50 wei);
        nSupportMoney += msg.value;
        addrPlayers.push(msg.sender);
        mapPlayer[msg.sender] = true;
    }
    
    function approveRequest(uint nArrayIndex) public{
        require(nArrayIndex < payRequests.length);
        PayRequest storage request = payRequests[nArrayIndex];
       
        require(mapPlayer[msg.sender]);
        require(payRequests[nArrayIndex].mapVote[msg.sender] == false);
        request.nAgreeCount += 1;
        payRequests[nArrayIndex].mapVote[msg.sender] = true;
    }
    
    
    
    // function approveRequest(uint nArrayIndex) public{
    //     require(nArrayIndex < payRequests.length);
    //     PayRequest storage request = payRequests[nArrayIndex];
        
    //     for(uint i = 0; i < addrPlayers.length; i++){
    //         if(addrPlayers[i] == msg.sender) {
    //             break;
    //         }
    //         if(i == addrPlayers.length - 1 /* && addrPlayers[i] != msg.sender*/){
    //             require(false);
    //         }
    //     }
        
        
    //     for(i =0; i < request.vctVotedAddr.length; i++){
    //         if(msg.sender == request.vctVotedAddr[i]){
    //             require(false);
    //         }
    //     }
        
    //     request.nAgreeCount += 1;
    //     request.vctVotedAddr.push(msg.sender);
    // }
    
    
    
    function finilizeRequest(uint nRequestIndex) public{
        PayRequest storage requst = payRequests[nRequestIndex];
        require(requst.bCompleted == false);
        require(requst.nAgreeCount * 2 > addrPlayers.length);
        
        
        //付款
        require(this.balance > requst.nPayment);
        requst.addrShop.transfer(requst.nPayment);
        requst.bCompleted = true;
    }
    
    
    
}