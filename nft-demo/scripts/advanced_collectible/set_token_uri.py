from scripts.helpful_scripts import OPENSEA_URL, get_account, get_breed
from brownie import AdvancedCollectible, network


dog_metadata_dic = {
    "PUG": "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json",
    "SHIBA_INU": "https://ipfs.io/ipfs/QmdryoExpgEQQQgJPoruwGJyZmz6SqV4FRTX1i73CT3iXn?filename=1-SHIBA_INU.json",
    "ST_BERNARD": "https://ipfs.io/ipfs/QmbBnUjyHHN7Ytq9xDsYF9sucZdDJLRkWz7vnZfrjMXMxs?filename=2-ST_BERNARD.json",
}


def main():
    print(f'Working in {network.show_active()}...')
    advanced_collectible = AdvancedCollectible[-1]
    no_of_collectibles = advanced_collectible.tokenCounter()
    print(f"You have {no_of_collectibles} collectibles")
    for token_id in range(no_of_collectibles):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        if not advanced_collectible.tokenURI(token_id).startswith("https://"):
            print(f'Setting token URI of {token_id}')
            set_token_uri(token_id, advanced_collectible,
                          dog_metadata_dic[breed])


def set_token_uri(token_id, nft_contract, tokenURI):
    account = get_account()
    tx = nft_contract.setTokenURI(token_id, tokenURI, {"from": account})
    tx.wait(1)
    print(
        f'Awesome! You can view your NFT at {OPENSEA_URL.format(nft_contract.address, token_id)}')
