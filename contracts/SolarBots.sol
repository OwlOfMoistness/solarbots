pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./MKToken.sol";
import "./MerkleWhitelist.sol";

/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"- 
*/

contract SolarBots is ERC721Enumerable, MerkleWhitelist, Ownable {
	using ECDSA for bytes32;

	uint256 public constant MAX_SUPPLY = 40000;
	uint256 public constant PRICE = 0.2 ether;
	uint256 public constant MAX_PER_CALL = 10;
	uint256 public constant PUBLIC_SALE = 1000;

	address public yieldToken;
	uint256 public publicSaleCounter;
	string public uri;

	mapping(address => uint256) public reservedToMint;
	mapping(address => uint256) public mintedBy;
	mapping(address => bool) public human;
	uint256 public reserved;
	uint256 public canPurchaseUnclaimed;
	uint256 public publicSaleDate;

	mapping(uint256 => uint256) genes;

	event BotMinted(uint256 indexed tokenId, address indexed receiver, uint256 genes);

	constructor(uint256 _canPurchaseUnclaimed, uint256 _publicSaleDate, bytes32 _root) ERC721("Solarbots", "BOTS") MerkleWhitelist(_root) {
		canPurchaseUnclaimed = _canPurchaseUnclaimed;
		publicSaleDate = _publicSaleDate;
	}

	function _baseURI() internal override view returns (string memory) {
		return uri;
	}

	function updateURI(string memory newURI) public onlyOwner {
		uri = newURI;
	}

	function updateYieldToken(address _token) external onlyOwner {
		yieldToken = _token;
	}

	function getReward() external {
		MkToken(yieldToken).updateReward(msg.sender, address(0), 0);
		MkToken(yieldToken).getReward(msg.sender);
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
		require(block.timestamp >= publicSaleDate, "Public sale not ready");
		require(_amount <= MAX_PER_CALL, "Minting too many at once");
		require(msg.value == _amount * PRICE, "Wrong price");

		uint256 supply = totalSupply();
		if (block.timestamp < canPurchaseUnclaimed){
			require(publicSaleCounter + _amount <= PUBLIC_SALE, "Over public sale amount");
			publicSaleCounter += _amount;
		}
		else
			require(supply + _amount * 4 <= MAX_SUPPLY - reserved * 4, "Can't mint over limit");

		MkToken(yieldToken).updateReward(msg.sender, address(0), 0);
		for (uint256 i = 0; i < _amount; i++)
			_mintTeam(supply + i * 4);
	}

	function reserveBots(uint256 _amount) external payable {
		require(block.timestamp >= publicSaleDate, "Public sale not ready");
		require(_amount <= MAX_PER_CALL, "Minting too many at once");
		require(msg.value == _amount * PRICE, "Wrong price");

		uint256 supply = totalSupply();
		if (block.timestamp < canPurchaseUnclaimed){
			require(publicSaleCounter + _amount <= PUBLIC_SALE, "Over public sale amount");
			publicSaleCounter += _amount;
		}
		else
			require(supply + _amount * 4 <= MAX_SUPPLY - reserved * 4, "Can't mint over limit");

		reservedToMint[msg.sender] += _amount;
		reserved += _amount;
	}

	function mintAllBotsWithSignature(uint256 _index, address _account, uint256 _amount, bytes32[] memory _proof) public payable {
		require(block.timestamp >= publicSaleDate, "Public sale not ready");
		require(msg.value == _amount * PRICE, "Wrong price");
		require(msg.sender == _account, "Caller not part of tree");
		require(mintedBy[_account] == 0, "Minted some");

		_claim(_index, _account, _amount, _proof);
		if (_amount > MAX_PER_CALL) {
			reservedToMint[_account] += _amount;
			reserved += _amount;
		}
		else {
			uint256 supply = totalSupply();
			for (uint256 i = 0; i < _amount; i++)
				_mintTeam(supply + i * 4);
		}
	}

	function mintSomeBotsWithSignature(uint256 _toMint, uint256 _index, address _account, uint256 _amount, bytes32[] memory _proof) public payable {
		require(block.timestamp >= publicSaleDate, "Public sale not ready");
		require(msg.value == _toMint * PRICE, "Wrong price");
		require(msg.sender == _account, "Caller not part of tree");

		require(!isClaimed(_index), "Claimed already");
		_verify(_index, _account, _amount, _proof);
		require(mintedBy[_account] + _toMint <= _amount, "Can't mint more than allocated");
		mintedBy[_account] += _toMint;
		if (_toMint > MAX_PER_CALL) {
			reservedToMint[_account] += _toMint;
			reserved += _toMint;
		}
		else {
			uint256 supply = totalSupply();
			for (uint256 i = 0; i < _toMint; i++)
				_mintTeam(supply + i * 4);
		}
	}

	function mintRemainder(uint256 _amount) external {
		require(_amount <= MAX_PER_CALL, "Minting too many at once");
		require(human[msg.sender], "No human :(");

		reservedToMint[msg.sender] -= _amount;
		reserved -= _amount;
		MkToken(yieldToken).updateReward(msg.sender, address(0), 0);
		uint256 supply = totalSupply();
		for (uint256 i = 0; i < _amount; i++)
			_mintTeam(supply + i * 4);
	}

	function transferMints(address _to, uint256 _amount) external {
		reservedToMint[msg.sender] -= _amount;
		reservedToMint[_to] += _amount;
	}

	function meHuman(string calldata _msg, bytes calldata _sig) external {
		require(keccak256(abi.encodePacked(_msg)).toEthSignedMessageHash().recover(_sig) == msg.sender, "Sig not valid");
		human[msg.sender] = true;
	}

	// gene composision
	// rarity    faction  bot-type   class
	// 00=00=00=00
	function _mintTeam(uint256 _id) internal {
		uint256 seed = generateSeed(0, _id);
		for(uint256 i = 0; i < 4; i++) {
			uint256 gene = 0;
			gene = gene + getRarityOutcome(seed) << 2;
			seed = generateSeed(seed, _id);
			uint256 faction = getFactionOutcome(seed);
			gene = (gene + faction) << 2;
			seed = generateSeed(seed, _id);
			// bot type
			if (faction == 0)
				gene <<= 2;
			else
				gene = (gene + 1 + seed % 3) << 2;
			seed = generateSeed(seed, _id);
			gene += i;
			_storeGenes(gene, _id + i);
			_mint(msg.sender, _id + i);
			emit BotMinted(_id + i, msg.sender, gene);
		}
	}

	function _storeGenes(uint256 _genes, uint256 _id) internal {
		uint256 word = _id / 32;
		uint256 index = _id % 32;
		genes[word] |= _genes << (index * 8);
	}

	function getGenes(uint256 _id) external view returns(uint256 gene) {
		uint256 word = _id / 32;
		uint256 index = _id % 32;
		gene = (genes[word] >> (index * 8)) & 0xff;
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

	function fetchEther() external onlyOwner {
		payable(msg.sender).transfer(address(this).balance);
	}
}