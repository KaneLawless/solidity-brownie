from brownie import Test, accounts


def main():
    account = accounts[0]
    test = Test.deploy({"from": account})

    rand, final = test._generateRandomDna("kane", {"from": account})
    print(rand)
    print(final)
