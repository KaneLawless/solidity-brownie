import eth_utils
from brownie import config, network, accounts, MockDai, MockWeth, MockV3Aggregator, Contract

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


contract_to_mock = {"weth_token": MockWeth,
                    "fau_token": MockDai,
                    "eth_usd_price_feed": MockV3Aggregator,
                    "dai_usd_price_feed": MockV3Aggregator}


def get_contract(contract_name):
    """This function will grab the contract addresses from bronwnie config if defined,
    otherwise it will deploy a mock version of that contract and return that mock contract.
        Args:
            contract_name(string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    # Check contract type
    contract_type = contract_to_mock[contract_name]

    # Deploying to local network:
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # Check if any mocks of this type are already deployed
            deploy_mocks()
        # Grab most recently deployed version of contract (i.e. Mock)
        contract = contract_type[-1]

    # Deploying on testnet
    else:
        contract_address = config["networks"][network.show_active(
        )][contract_name]
        # address and ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi)

    return contract


DECIMALS = 18
INITIAL_VALUE = 2000000000000000000000


def deploy_mocks():
    """
    Use this script if you want to deploy mocks to a testnet
    """

    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock WethToken...")
    weth_token = MockWeth.deploy({"from": account})
    print("Deploying Mock Dai token...")
    dai_token = MockDai.deploy({"from": account})
    print("Deploying Mock Price feed....")
    mock_price_feed = MockV3Aggregator.deploy(
        DECIMALS, INITIAL_VALUE, {"from": account})
    print(f"Deployed to {mock_price_feed.address}")
