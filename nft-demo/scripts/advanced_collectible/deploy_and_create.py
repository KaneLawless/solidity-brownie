from scripts.helpful_scripts import fund_with_link, get_account, OPENSEA_URL, get_contract
from brownie import AdvancedCollectible, config, network


sample_token_uri = "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"


def deploy_and_create():
    account = get_account()
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False)
    )

    fund_with_link(advanced_collectible.address)
    creation_tx = advanced_collectible.createCollectible({"from": account})
    creation_tx.wait(1)
    print("New token has been created")
    return advanced_collectible, creation_tx


def main():
    deploy_and_create()
