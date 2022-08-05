from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, get_breed
import pytest
from brownie import network
from scripts.advanced_collectible.deploy_and_create import deploy_and_create


def test_can_create_advanced_collectible():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    advanced_collectible, creation_tx = deploy_and_create()

    # Need to simluate the randomness being returned by the VRF coordinator / Chainlink node
    requestId = creation_tx.events["requestedCollectible"]["requestId"]
    random_number = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, random_number, advanced_collectible.address, {"from": get_account()})

    # Assert a token was created and that the breed is correct
    assert advanced_collectible.tokenCounter() == 1
    assert advanced_collectible.tokenIdToBreed(0) == random_number % 3


def test_get_breed():
    # Arrange / Act
    breed = get_breed(0)
    # Assert
    assert breed == "PUG"
