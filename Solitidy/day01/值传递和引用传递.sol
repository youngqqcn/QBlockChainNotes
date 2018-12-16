pragma solidity ^0.4.20;



contract Student{
    
    uint _score = 50;
    string _name = "lily";
    
    
    //值传递
    // function changeName(string memory name) public{
    //     _name = name;
    // }
    
    //引用传递
    function changeName(string storage name) private{
        bytes(name)[0] = 'L';
        _name = name;
    }
    
    function getName()public returns(string) {
        
        return _name;
    }
    
    function execute() public{
       // string tmp = "happy";
        changeName(_name);
        //changeName("happy");
        changeScore(_score);
    }
    
    function changeScore(uint score) private{
        _score = 90;
    }
    
    function getScore() view public returns(uint){
        return _score;
    }
    
    
}