pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"- 
*/

contract MkToken is ERC20("MK", "MK1") {

	uint256 constant public BASE_RATE = 6_849315068_000000000 ; 

	// CHANGE THIS BEFORE LIVE
	uint256 constant public END = 1931622407;

	mapping(address => uint256) public rewards;
	mapping(address => uint256) public lastUpdate;

	IERC721 public  mkContracts;

	event RewardPaid(address indexed user, uint256 reward);

	constructor(address _mk) public{
		mkContracts = IERC721(_mk);
	}

	function min(uint256 a, uint256 b) internal pure returns (uint256) {
		return a < b ? a : b;
	}

	// called on transfers
	function updateReward(address _from, address _to, uint256 _tokenId) external {
		require(msg.sender == address(mkContracts));
		uint256 time = min(block.timestamp, END);
		uint256 timerFrom = lastUpdate[_from];
		if (timerFrom > 0)
			rewards[_from] += mkContracts.balanceOf(_from) * BASE_RATE * (time - timerFrom) / 86400;
		if (timerFrom != END)
			lastUpdate[_from] = time;
		if (_to != address(0)) {
			uint256 timerTo = lastUpdate[_to];
			if (timerTo > 0)
				rewards[_to] += mkContracts.balanceOf(_to) * BASE_RATE * (time - timerFrom) / 86400;
			if (timerTo != END)
				lastUpdate[_to] = time;
		}
	}

	function getReward(address _to) external {
		require(msg.sender == address(mkContracts));
		uint256 reward = rewards[_to];
		if (reward > 0) {
			rewards[_to] = 0;
			_mint(_to, reward);
			emit RewardPaid(_to, reward);
		}
	}

	function burn(address _from, uint256 _amount) external {
		_burn(_from, _amount);
	}

	function getTotalClaimable(address _user) external view returns(uint256) {
		uint256 time = min(block.timestamp, END);
		uint256 pending = mkContracts.balanceOf(_user) * BASE_RATE * (time - lastUpdate[_user]) / 86400;
		return rewards[_user] + pending;
	}
}
