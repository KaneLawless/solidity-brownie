from brownie import SimpleStorage, accounts, config


def read_contract():

    # Most recently deployed contract address ( [0] for the first deployment)
    simple_storage = SimpleStorage[-1]

    # To interact with a contract, we need to know ABI and address but BROWNIE already knows these
    # Will call and return directly from chain
    print(simple_storage.retrieve())


def main():
    read_contract()
