from scripts.helpful_scripts import encode_function_data, get_account, upgrade
from brownie import exceptions, Box, BoxV2, ProxyAdmin, TransparentUpgradeableProxy, Contract
import pytest


def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initialiser_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address, proxy_admin.address, box_encoded_initialiser_function, {
            "from": account, "gas_limit": 1000000})

    box_v2 = BoxV2.deploy({"from": account})

    # Assign the abi of the box v2 contract to the proxy address
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)

    # Increment should revert because we havent upgraded to v2 yet
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})

    # upgrade
    upgrade(account, proxy, box_v2, proxy_admin)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
