// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface GetBalanceOf {
    function balanceOf(address account) external view returns (uint);
}

contract MyToken is GetBalanceOf {
    uint immutable totalTokens;
    address immutable owner;
    mapping(address => uint) balances;

    modifier enoughTokens(address _from, uint _amount) {
        require(balanceOf(_from) >= _amount, "not enough tokens!");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not an owner!");
        _;
    }

    constructor(
        uint initialSupply
    ) {
        totalTokens = initialSupply;
        owner = msg.sender;
        balances[owner] += initialSupply;
    }

    function totalSupply() public view returns (uint) {
        return totalTokens;
    }

    function balanceOf(address account) public view returns (uint) {
        return balances[account];
    }

    function transfer(
        address to,
        uint amount
    ) external enoughTokens(msg.sender, amount) {
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}

contract Governance {

    struct ProposalVote {
        mapping(address => bool) hasVoted;
        uint againstVotes;
        uint forVotes;
        uint abstainVotes;
        bool exists;
    }

    mapping(bytes32 => ProposalVote) public proposalVotes;
    GetBalanceOf public token;

    constructor(address target_contractken) {
        token = GetBalanceOf(target_contractken);
    }

    function getProposalHash(
        address target_contract,
        uint _value,
        string calldata _func,
        bytes calldata _data,
        string calldata _description
    ) external pure returns (bytes32) {
        return  keccak256(abi.encode(target_contract, _value, _func, _data, keccak256(bytes(_description))));
    }

    function propose(
        address target_contract,
        uint _value,
        string calldata _func,
        bytes calldata _data,
        string calldata _description
    ) external returns (bytes32) {
        require(token.balanceOf(msg.sender) > 0, "not enough tokens");
        bytes32 proposalId = this.getProposalHash(target_contract, _value, _func, _data, _description);
        require(proposalVotes[proposalId].exists == false);
        proposalVotes[proposalId].exists = true;
        return proposalId;
    }

    function execute(
        address target_contract,
        uint _value,
        string calldata _func,
        bytes calldata _data,
        string calldata _description
    ) external returns (bytes memory) {
        bytes32 proposalId = this.getProposalHash(target_contract, _value, _func, _data, _description);
        require(proposalSucceded(proposalId));
        proposalVotes[proposalId].exists = true;
        bytes memory data;
        if (bytes(_func).length > 0) {
            data = abi.encodePacked(bytes4(keccak256(bytes(_func))), _data);
        } else {
            data = _data;
        }
        (bool success, bytes memory resp) = target_contract.call{value: _value}(data);
        require(success, "tx failed");
        return resp;
    }

    function vote(bytes32 proposalId, uint8 voteType) external {
        
        uint votingPower = token.balanceOf(msg.sender);
        require(votingPower > 0, "not enough tokens");
        ProposalVote storage proposalVote = proposalVotes[proposalId];
        require(!proposalVote.hasVoted[msg.sender], "already voted");
        if (voteType == 0) {
            proposalVote.againstVotes += votingPower;
        } else if (voteType == 1) {
            proposalVote.forVotes += votingPower;
        } else {
            proposalVote.abstainVotes += votingPower;
        }
        proposalVote.hasVoted[msg.sender] = true;
    }

    function proposalSucceded(bytes32 proposalId) public view returns (bool) {
        ProposalVote storage proposal = proposalVotes[proposalId];
        return proposal.forVotes > proposal.againstVotes;
    }

    receive() external payable {}
}

contract TargetContract {
    constructor() {}

    function sayHello() external pure returns (string memory)  {
        return "Hello, world";
    }
}
