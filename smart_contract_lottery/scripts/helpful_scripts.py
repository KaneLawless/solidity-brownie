from brownie import accounts, config, network, MockV3Aggregator, Contract, VRFCoordinatorMock, LinkToken

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # If index provided, then use brownie account of that index
    # If id provided, load account from that id
    # Else check network is local or forked and return accounts[0]
    # All else failing, add account from private key in env file
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}


def get_contract(contract_name):
    """This function will grab the contract addresses from bronwi config if defined,
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


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    vrf_coordinator = VRFCoordinatorMock.deploy(
        link_token.address, {"from": account})

    print("Deployed Mocks")


def fund_with_link(contract_addr, account=None, link_token=None, amount=100000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_addr, amount, {"from": account})
    tx.wait(1)
    print("Contract funded")
    return tx
