pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./MKToken.sol";
import "./MerkleWhitelist.sol";

/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"- 
*/

contract SolarBots is ERC721Enumerable, MerkleWhitelist, Ownable{

	uint256 public constant MAX_SUPPLY = 40000;
	uint256 public constant PRICE = 0.2 ether;
	uint256 public constant MAX_PER_CALL = 10;
	uint256 public constant PUBLIC_SALE = 1000;

	address public yieldToken;
	uint256 public publicSaleCounter;
	string public uri;

	mapping(address => uint256) public reservedToMint;
	uint256 public reserved;
	bool public canPurchaseUnclaimed;

	mapping(uint256 => uint256) genes;

	constructor(address _recipient, bytes32 _root) ERC721("Solar Bots", "BOTS") MerkleWhitelist(_root) {
	}

	function _baseURI() internal override view returns (string memory) {
        return uri;
    }

	function updateURI(string memory newURI) public onlyOwner {
		uri = newURI;
	}

	function setCanPurchaseUnclaimed(bool _val) external onlyOwner {
		canPurchaseUnclaimed = _val;
	}

	function transferFrom(address from, address to, uint256 tokenId) public override {
		MkToken(yieldToken).updateReward(from, to, tokenId);
		ERC721.transferFrom(from, to, tokenId);
	}

	function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory _data) public override {
		MkToken(yieldToken).updateReward(from, to, tokenId);
		ERC721.safeTransferFrom(from, to, tokenId, _data);
	}

	function mintBots(uint256 _amount) external payable {
		require(_amount < MAX_PER_CALL, "Minting too many at once");
		require(msg.value == _amount * PRICE, "Wrong price");
		require(publicSaleCounter + _amount < PUBLIC_SALE, "Over public sale amount");

		MkToken(yieldToken).updateReward(msg.sender, address(0), 0);
		uint256 supply = totalSupply();
		for (uint256 i = 0; i < _amount; i++)
			_mintTeam(supply + i * 4);
		publicSaleCounter += _amount;
	}

	function mintUnclaimed(uint256 _amount) external payable {
		require(canPurchaseUnclaimed, "Cannot purchase unclaimed");
		require(_amount < MAX_PER_CALL, "Minting too many at once");
		require(msg.value == _amount * PRICE, "Wrong price");
		uint256 supply = totalSupply();
		require(supply + _amount * 4 < MAX_SUPPLY, "Can't mint over limit");

		MkToken(yieldToken).updateReward(msg.sender, address(0), 0);
		for (uint256 i = 0; i < _amount; i++)
			_mintTeam(supply + i * 4);
	}

	function mintBotsWithSignature(uint256 _index, address _account, uint256 _amount, bytes32[] memory _proof) public payable {
		require(msg.value == _amount * PRICE, "Wrong price");

		_claim(_index, _account, _amount, _proof);
		if (_amount > MAX_PER_CALL) {
			reservedToMint[_account] = _amount;
		}
		else {
			uint256 supply = totalSupply();
			for (uint256 i = 0; i < _amount; i++)
				_mintTeam(supply + i * 4);
		}
	}

	function mintRemainder(uint256 _amount) external {
		require(_amount < MAX_PER_CALL, "Minting too many at once");

		reservedToMint[msg.sender] -= _amount;
		MkToken(yieldToken).updateReward(msg.sender, address(0), 0);
		uint256 supply = totalSupply();
		for (uint256 i = 0; i < _amount; i++)
			_mintTeam(supply + i * 4);
	}


	// gene composision
	// 1       8        16       24      
	// 0000000 - 00000000-00000000 - 000000000
	// rarity    faction  bot-type   class
	function _mintTeam(uint256 _id) internal {
		uint256 seed = generateSeed(0, _id);
		for(uint256 i = 0; i < 4; i++) {
			uint256 gene = 0;
			gene = gene + getRarityOutcome(seed) << 64;
			seed = generateSeed(seed, _id);
			uint256 faction = getFactionOutcome(seed);
			gene = (gene + faction) << 64;
			seed = generateSeed(seed, _id);
			// bot type
			if (faction == 0)
				gene <<= 64;
			else
				gene = (gene + 1 + seed % 3) << 64;
			seed = generateSeed(seed, _id);
			gene += i;
			genes[_id + i] = gene;
			_mint(msg.sender, _id + i);
		}
	}

	function getFactionOutcome(uint256 _seed) internal returns(uint256) {
		uint256 range = _seed % 100;
		// 10% - neutral
		if (range < 10)
			return 0;
		// 30% - lacrean
		else if (range < 40)
			return 1;
		// 30% - iilskagaard
		else if (range < 70)
			return 2;
		// 30% - arboria
		else
			return 3;
	}

	function getRarityOutcome(uint256 _seed) internal returns(uint256) {
		uint256 range = _seed % 10000;
		// 0.25% - void
		if (range < 25)
			return 0;
		// 12.5% - epic
		else if (range < 1275)
			return 1;
		// 25% - rare
		else if (range < 3775)
			return 2;
		// 62.25% - common
		else
			return 3;
	}

	function generateSeed(uint256 _seed, uint256 _id) internal view returns (uint256) {
		if (_seed == 0)
			return uint256(keccak256(abi.encodePacked(block.difficulty, block.timestamp, _id)));
		else
			return uint256(keccak256(abi.encodePacked(_seed)));
	}

	function fetchEther() external onlyOwner{
		payable(msg.sender).transfer(address(this).balance);
	}

}