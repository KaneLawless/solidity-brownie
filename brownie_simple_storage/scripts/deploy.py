from brownie import accounts, config, SimpleStorage, network


def deploy_simple_storage():
    # Method 1
    # account = accounts[0]
    # Method 2
    # account = accounts.load("MetaMask2")
    # print(account)
    # Method 3
    # account = accounts.add(os.getenv("PRIVATE_KEY"))
    # print(account)
    # Method 4
    # # account = accounts.add(config["wallets"]["from_key"])
    # print(account)

    account = get_account()

    simple_storage = SimpleStorage.deploy(
        {"from": account})  # deploy returns a contrcat object

    # Don't need "from" because its a call (brownie knows)
    # Calling "retrieve" function from the contract
    stored_value = simple_storage.retrieve()
    print(stored_value)

    transaction = simple_storage.store(7, {"from": account})
    transaction.wait(1)  # No. of blocks to wait for confirmation
    updated_value = simple_storage.retrieve()
    print(updated_value)


def get_account():
    # Check if we are on a development network or not, and return correct account
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def main():
    deploy_simple_storage()
