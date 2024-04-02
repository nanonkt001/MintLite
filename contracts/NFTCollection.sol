// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NFTCollection is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    constructor() ERC721("MintLiteNFT", "MLNFT") {}

    function mint(address to, string memory tokenURI) external onlyOwner returns (uint256) {
        uint256 tokenId = ++nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        return tokenId;
    }

    function batchMint(address to, string[] calldata tokenURIs) external onlyOwner returns (uint256[] memory) {
        uint256[] memory minted = new uint256[](tokenURIs.length);
        for (uint256 i = 0; i < tokenURIs.length; i++) {
            uint256 tokenId = ++nextTokenId;
            _safeMint(to, tokenId);
            _setTokenURI(tokenId, tokenURIs[i]);
            minted[i] = tokenId;
        }
        return minted;
    }
}
