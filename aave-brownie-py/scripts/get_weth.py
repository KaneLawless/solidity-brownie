from scripts.helpful_scrips import get_account
from brownie import interface, config, network


def main():
    get_weth()


def get_weth():
    """
    Mints WETH by depositing ETH
    """
    # To interact:  ABI and Address
    account = get_account()
    # Below compiles to the contract ABI
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.01 * 10**18})
    tx.wait(1)
    print('receieved 0.1 WETH')
    return tx
