from brownie import AdvancedCollectible, network
from scripts.helpful_scripts import get_breed
from metadata.sample_metadata import metadata_template
from pathlib import Path
import requests
import json


def main():
    advanced_collectible = AdvancedCollectible[-1]
    number_of_collectibles_created = advanced_collectible.tokenCounter()
    print(f'You have created {number_of_collectibles_created} collectibles')
    for token_id in range(number_of_collectibles_created):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        metadata_file_name = (
            f'./metadata/{network.show_active()}/{token_id}-{breed}.json'
        )

        collectible_metadata = metadata_template

        if Path(metadata_file_name).exists():
            print(f'{metadata_file_name} already exists')
        else:
            print(f'Creating metadata filename {metadata_file_name}')
            collectible_metadata["name"] = breed
            collectible_metadata["description"] = f'An adorable {breed} pup!'
            image_file_name = "./img/" + breed.lower().replace("_", "-") + ".png"
            image_uri = upload_to_ipfs(image_file_name)
            collectible_metadata["image"] = image_uri
            with open(metadata_file_name, "w") as f:
                json.dump(collectible_metadata, f)
            upload_to_ipfs(metadata_file_name)


def upload_to_ipfs(filepath):
    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()
        # upload to ipfs
        # need to start ipfs daemon first to get url "ipfs init, ipfs daemon"
        ipfs_url = "http://127.0.0.1:5001"
        # endpoint to make a POST request
        endpoint = "/api/v0/add"
        response = requests.post(
            ipfs_url + endpoint, files={"file": image_binary})
        ipfs_hash = response.json()["Hash"]
        # Split filname to get the last part e.g. "./img/0-Pug.png" -> "0-Pug.png"
        filename = filepath.split("/")[-1:][0]
        image_uri = f'https://ipfs.io/ipfs/{ipfs_hash}?filename={filename}'
        print(image_uri)
        return image_uri
