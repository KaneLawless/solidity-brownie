from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3
import yaml
import json
import shutil
import os

KEPT_BALANCE = Web3.toWei("100", "ether")


def deploy_token_farm_and_dapp_token(front_end_update=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        dapp_token.address, {"from": account}, publish_source=config["networks"][network.show_active()].get("verify"))
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account})
    tx.wait(1)

    # Allow 3 tokens: dapp token, weth token, FAU token (fake Dai)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")

    # Map token addresses to price feed addresses. Dapp and Fau tokens will be equal to the Dai price. Weth == ETH
    dict_of_allowed_tokens = {
        dapp_token:  get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed")
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    if front_end_update:
        update_front_end()

    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedAddress(
            token.address, dict_of_allowed_tokens[token], {"from": account})
        set_tx.wait(1)


def update_front_end():
    # Copy build folder
    copy_folders_to_front_end("./build", "./front-end/src/chain-info")

    # Copy config
    # Typescript doesn't work too well with yaml, so convert to json first
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front-end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtee(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_dapp_token(front_end_update=True)
