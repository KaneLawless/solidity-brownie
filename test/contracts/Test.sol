// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Test {
    uint256 dnaModulus = 10**16;

    function _generateRandomDna(string memory _str)
        public
        view
        returns (uint256, uint256)
    {
        uint256 rand = uint256(keccak256(abi.encodePacked(_str)));
        return (rand, rand % dnaModulus);
    }
}
