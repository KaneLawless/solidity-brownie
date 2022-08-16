from lib2to3.pgen2 import token
from scripts.deploy import deploy_token_farm_and_dapp_token
from scripts.helpful_scripts import DECIMALS, INITIAL_VALUE, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from brownie import TokenFarm, DappToken, MockDai, network, exceptions
import pytest
from web3 import Web3


def test_set_price_feed_contract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("only for local testing")

    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    price_feed_address = get_contract("eth_usd_price_feed")

    # Act
    token_farm.setPriceFeedAddress(
        dapp_token.address, price_feed_address, {"from": account})

    # Assert
    assert token_farm.tokenPriceFeedMapping(
        dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedAddress(
            dapp_token.address, price_feed_address, {"from": non_owner})


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    account = get_account()

    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(
        amount_staked, dapp_token.address, {"from": account})

    assert token_farm.stakingBalance(
        dapp_token.address, account.address) == amount_staked
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address

    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    # Act
    token_farm.issueTokens({"from": account})

    # We set initial value in our Mock V3 Aggregator for ETH to be 1 Eth : 2000*10**18
    # So we would expect that staking 1 Dapp token should receive 2000 Dapp tokens in return because the price of Eth is 2000
    assert dapp_token.balanceOf(
        account.address) == starting_balance + INITIAL_VALUE


def test_get_user_total_value(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    mock_dai_token = MockDai[-1]
    amount_to_stake_dai = amount_staked * 2
    mock_dai_token.approve(token_farm.address,
                           amount_to_stake_dai, {"from": account})
    token_farm.stakeTokens(amount_to_stake_dai,
                           mock_dai_token, {"from": account})
    assert token_farm.uniqueTokensStaked(account.address) == 2
    assert token_farm.getUserTotalValue(account.address) == INITIAL_VALUE * 3


def test_get_user_single_token_value(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    assert token_farm.getUserSingleTokenValue(
        account.address, dapp_token, {"from": account}) == 0
    dapp_token.approve(token_farm, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token, {"from": account})
    assert token_farm.getUserSingleTokenValue(
        account.address, dapp_token) == INITIAL_VALUE


def test_get_token_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    expected_response = (INITIAL_VALUE, DECIMALS)
    actual_response = token_farm.getTokenValue(dapp_token.address)
    assert expected_response == actual_response


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    balance_before = dapp_token.balanceOf(account.address)
    token_farm.unstakeTokens(dapp_token.address, {"from": account})
    balance_after = dapp_token.balanceOf(account.address)
    assert balance_after == balance_before + amount_staked
    assert token_farm.stakingBalance(dapp_token.address, account.address) == 0
    assert token_farm.uniqueTokensStaked(account.address) == 0


def test_token_is_allowed():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    assert token_farm.tokenIsAllowed(dapp_token.address) == True


def test_add_allowed_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("For local networks only")
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(dapp_token.address, {"from": account})
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    assert token_farm.allowedTokens(0) == dapp_token.address
