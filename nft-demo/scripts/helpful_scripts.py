from brownie import accounts, network, config, Contract, LinkToken, VRFCoordinatorMock
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development", "ganache-local", "mainnet-fork", "mainnet-fork-dev"]
OPENSEA_URL = "https://testnets.opensea.io/assets/rinkeby/{}/{}"
BREED_MAPPING = {0: "PUG", 1: "SHIBU_INU", 2: "ST_BERNARD"}


def get_breed(breed_number):
    return BREED_MAPPING[breed_number]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS

    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {"link_token": LinkToken,
                    "vrf_coordinator": VRFCoordinatorMock}


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


def deploy_mocks():
    """
    Use this script if you want to deploy mocks to a testnet
    """

    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"Link Token deployed to {link_token.address}")
    print("Deploying Mock VRF Coordinator...")
    vrf_coordinator = VRFCoordinatorMock.deploy(
        link_token.address, {"from": account})
    print(f"VRFCoordinator deployed to {vrf_coordinator.address}")
    print("All done!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.1, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(
        contract_address, amount, {"from": account})
    funding_tx.wait(1)
    print(f"Funded {contract_address}")
    return funding_tx
