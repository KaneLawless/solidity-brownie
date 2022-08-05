from tracemalloc import start
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery, get_account, fund_with_link, get_contract
from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS
import pytest


def test_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # We set ETH price to 2000 in helpful scripts and USD 50 as entrance fee in the contract
    # 50/2000 = 0.025 ETH expected value
    expected = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter(
            {"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery, account)
    lottery.endLottery({"from": account})
    assert lottery.lotteryState() == 2  # CALCULATING_WINNER


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1),
                  "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2),
                  "value": lottery.getEntranceFee()})
    fund_with_link(lottery)

    starting_bal = account.balance()
    lottery_balance = lottery.balance()

    # After funding with LINK, Lottery sends a request to a chainlink link for randomness
    # Since this is a unit test on a dev net, we need to simulate the response
    tx = lottery.endLottery({"from": account})

    # Lottery emits an event including the requestId so we can use it later
    requestId = tx.events["RequestedRandomness"]["requestId"]

    # Defined randomness for testing
    STATIC_RNG = 777

    # Mock response from chainlink link for request for randomness
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RNG, lottery.address, {"from": account})

    # Find the winner: randomness (static_rng) % len(players) ==> 777 % 3 == 0. Winner should be account[0]
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_bal + lottery_balance
