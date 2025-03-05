// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Election {
    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    address public owner;
    bool public goingon = true;
    mapping(address => bool) public voters;
    mapping(uint => Candidate) public candidates;
    uint public candidatesCount;

    event VotedEvent(uint indexed _candidateId);
    event ElectionReset();

    constructor() {
        owner = msg.sender; // Set the contract deployer as the owner
        addCandidate("ASHIK JENLY");
        addCandidate("BRIJESH A");
        addCandidate("PRADEEP M");
        addCandidate("Candidate 4");
        addCandidate("Candidate 5");
        addCandidate("Candidate 6");
        addCandidate("Candidate 7");
        addCandidate("Candidate 8");
        addCandidate("Candidate 9");
        addCandidate("Candidate 10");
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function");
        _;
    }

    function addCandidate(string memory _name) private {
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
    }

    function end() public onlyOwner {
        goingon = false;
    }

    function vote(uint _candidateId) public {
        require(!voters[msg.sender], "Already voted");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate");
        require(goingon, "Election ended");

        voters[msg.sender] = true;
        candidates[_candidateId].voteCount++;

        emit VotedEvent(_candidateId);
    }

    function resetElection() public onlyOwner {
        // Reset the voters mapping
        for (uint i = 1; i <= candidatesCount; i++) {
            candidates[i].voteCount = 0;
        }

        for (uint i = 1; i <= candidatesCount; i++) {
            delete voters[address(uint160(i))];
        }

        goingon = true;
        emit ElectionReset();
    }
}
