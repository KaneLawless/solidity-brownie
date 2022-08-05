import eth_utils
from brownie import config, network, accounts

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development", "ganache-local", "mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


# initialiser = a function
# encode_function_data encodes the initialiser and args to bytes so that the SC knows which function to call
# If args or initialiser are blank, returns an empty hex string
def encode_function_data(initialiser=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initialiser:
        return eth_utils.to_bytes(hexstr="0x")
    return initialiser.encode_input(*args)


def upgrade(
    account,
    proxy,
    new_implentation_address,
    proxy_admin_contract=None,
    initialiser=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initialiser:
            encoded_function_call = encode_function_data(initialiser, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implentation_address,
                encode_function_data,
                {"from": account}
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, new_implentation_address, {"from": account})
    else:
        if initialiser:
            encoded_function_call = encode_function_data(initialiser, *args)
            transaction = proxy.upgradeToAndCall(
                new_implentation_address, encoded_function_call, {"from": account})
        else:
            transaction = proxy.upgradeTo(
                new_implentation_address, {"from": account})
    return transaction
