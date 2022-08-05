import web3
from brownie import FundMe, accounts, network, config, MockV3Aggregator
from scripts.helpful_scripts import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from web3 import Web3


def deploy_fund_me():
    account = get_account()
    # Pass contructor variables before 'from' in deploy method
    # This method is best for persistent netwoks. Otherwise we should deploy 'Mocks'
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active(
        )]["eth_usd_price_feed"]

    # If development, deploy Mocks. Mocks stored in ./contracts/tests (need to import into this file)
    else:
        deploy_mocks()
        # Use latest deployed version
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"))
    print(f'Contract deployed to {fund_me.address}')
    
    return fund_me


def main():
    deploy_fund_me()
