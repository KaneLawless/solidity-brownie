from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from scripts.deploy import deploy_token_farm_and_dapp_token
from brownie import network
import pytest


def test_stake_and_issue(amount_staked):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Not for local testing...")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    dapp_token.approve(token_farm, amount_staked, {"from": account})
    stake_tx = token_farm.stakeTokens(
        amount_staked, dapp_token.address, {"from": account})
    stake_tx.wait(1)
    balance_before = dapp_token.balanceOf(account.address)
    print(f'Balance before issue: {balance_before}')
    price_feed = get_contract("dai_usd_price_feed")
    (_, price, _, _, _) = price_feed.latestRoundData()
    total_amount_to_issue = (
        price / 10 ** price_feed.decimals()) * amount_staked
    print(f'Total value of staked tokens: {total_amount_to_issue}')
    issue_tx = token_farm.issueTokens({"from": account})
    issue_tx.wait(1)
    balance_after = dapp_token.balanceOf(account.address)
    print(f'Balance after: {balance_after}')
    assert balance_after == balance_before + total_amount_to_issue
