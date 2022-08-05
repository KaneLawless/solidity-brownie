from brownie import OurToken, network, config
from scripts.helpful_scripts import get_account
from web3 import Web3


initial_supply = Web3.toWei("100", "ether")


def deploy_ERC20():
    account = get_account()
    token = OurToken.deploy(
        initial_supply, {"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))


def main():
    deploy_ERC20()
