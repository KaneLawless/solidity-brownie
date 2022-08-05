from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        # Returns a Mock price feed if one is already deployed
        # Else will deploy a Mock for us and return it
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False)
    )
    print("Deployed Lottery!")

    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Started Lottery!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # add some extra in case of rounding or simple errors
    value = lottery.getEntranceFee() + 1000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    # fund the contract with Link token
    tx = fund_with_link(lottery.address)
    tx.wait(1)

    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)

    time.sleep(180)
    print(f'{lottery.recentWinner()} is the new winner!')


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
