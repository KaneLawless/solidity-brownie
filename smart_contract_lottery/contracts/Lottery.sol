// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 public usdEntranceFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    address public recentWinner;
    uint256 public randomness;

    // Enumerate different states (open=0, closed=1 etc)
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    // After creating enum LOTTERY_STATE, we can create a variable of type LOTTERY_STATE
    LOTTERY_STATE public lotteryState;

    uint256 public fee;
    bytes32 public keyhash;

    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntranceFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        // Initialise lottery state to be closed, so we can "open" it.
        lotteryState = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        // 50 usd min
        require(
            lotteryState == LOTTERY_STATE.OPEN,
            "Lottery has not yet begun"
        );
        require(msg.value >= getEntranceFee(), "You need to spend more ETH");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10; // fix uint256 and decimals
        uint256 costToEnter = (usdEntranceFee * 10**18) / adjustedPrice; // * by 10^18 first to avoid working with decimals
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lotteryState == LOTTERY_STATE.CLOSED,
            "Lottery has already begun"
        );
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        require(lotteryState == LOTTERY_STATE.OPEN, "Lottery must be ongoing");
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(lotteryState == LOTTERY_STATE.CALCULATING_WINNER, "not yet");
        require(_randomness > 0, "no randomness found");

        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        payable(recentWinner).transfer(address(this).balance);

        // Reset
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
        randomness = _randomness; // Keep track of most recent randomness
    }
}
