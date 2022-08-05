from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import Box, ProxyAdmin, TransparentUpgradeableProxy, BoxV2, network, Contract


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}... ")
    box = Box.deploy({"from": account}, publish_source=True)
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    #initialiser = box.store, 1
    box_encoded_initialiser_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.address, box_encoded_initialiser_function, {"from": account, "gas_limit": 1000000}, publish_source=True)

    print(f'Proxy deployed to {proxy}, you can now upgrade to v2 !')

    # Assign the abi of the box contract to the proxy address
    # This works because the proxy will delegate all calls to the Box contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    print(proxy_box.retrieve())
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # beginning upgrade
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(account, proxy, box_v2, proxy_admin)
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded")

    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})

    # Retrieve should now return 2. The value was stored and remained in the proxy during the upgrade!
    print(proxy_box.retrieve())
