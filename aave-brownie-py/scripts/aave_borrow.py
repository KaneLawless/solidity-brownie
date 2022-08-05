from scripts.helpful_scrips import get_account
from brownie import network, config, interface
from scripts.get_weth import get_weth
from web3 import Web3


amount = Web3.toWei(0.01, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    # if network.show_active() in ["mainnet-fork"]:
    get_weth()
    # ABI and Address
    lending_pool = get_lending_pool()
    # Approve sending ERC20
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(erc20_address, amount,
                              account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    print("Lets borrow some DAI !")
    # Need to get DAI price in terms of ETH - chainlink price feeds

    dai_eth_price_feed = config["networks"][network.show_active(
    )]["dai_eth_price_feed"]
    dai_eth_price = get_asset_price(dai_eth_price_feed)

    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # eth price in DAI * borrowable eth * 0.95 to give a bit of safety from liquidation

    print(f"Borrowing {amount_dai_to_borrow} Dai....")
    dai_token = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(dai_token,
                                    Web3.toWei(amount_dai_to_borrow, "ether"), 1, 0, account, {"from": account})
    borrow_tx.wait(1)

    get_borrowable_data(lending_pool, account)
    #repay_all(amount_dai_to_borrow, lending_pool, account)
    #get_borrowable_data(lending_pool, account)


def repay_all(amount, lending_pool, account):
    token_addr = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(
        Web3.toWei(amount, "ether"), lending_pool, token_addr, account)
    print("Approval transaction sent")
    repay_tx = lending_pool.repay(
        token_addr,
        Web3.toWei(amount, "ether"),
        1,
        account,
        {"from": account})
    repay_tx.wait(1)
    print("Debt repayed!")


def get_asset_price(price_feed_address):
    # ABI and Address
    dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]  # in Wei
    price_in_eth = Web3.fromWei(latest_price, "ether")
    print(f'DAI/ETH latest price is {price_in_eth}')

    return float(price_in_eth)


def get_borrowable_data(lending_pool, account):
    (total_collateral_eth,
     total_debt_eth,
     available_borrow_eth,
     current_liquidation_threshold,
     ltv,
     health_factor) = lending_pool.getUserAccountData(account)

    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")

    print(f'You have {total_collateral_eth} worth of ETH deposited')
    print(f'You have {available_borrow_eth} worth of ETH available to borrow')
    print(f'You have {total_debt_eth} worth of ETH debt')

    return (float(available_borrow_eth), float(total_debt_eth))


def get_lending_pool():
    # Get ABI of address provider, to provide the lending pool address
    lending_pool_address_provider = interface.ILendingPoolAddressProvider(
        config["networks"][network.show_active(
        )]["lending_pool_address_provider"]
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    # Get ABI of Lending Pool now
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    # abi and address
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("approved!")
