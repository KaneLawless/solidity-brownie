import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


install_solc("0.6.0")
# Compile solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        }
    },
    solc_version="0.6.0",
)

with open("./compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


w3 = Web3(Web3.HTTPProvider(
    "https://rinkeby.infura.io/v3/ef681304177c4045b1d8d049702037aa"))
chain_id = 4
my_addr = "0x"
pk = os.getenv("PRIVATE_KEY")

# Create contract in Py
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
print(SimpleStorage)  # class web3....contract

# Get latest txn count
nonce = w3.eth.getTransactionCount(my_addr)
print(nonce)

# Build, sign, send
txn = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_addr,
        "nonce": nonce
    }
)

stxn = w3.eth.account.sign_transaction(txn, private_key=pk)

print(stxn)
print("Deploying contract....")
# send
txn_hash = w3.eth.send_raw_transaction(stxn.rawTransaction)

# wait for confirmation
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print(" Deployed Successfully")
# Working with a contract we need address & abi
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)

# Interacting with contract => Call or Transact
print("Original 'favourite number' value: ")
print(simple_storage.functions.retrieve().call())  # calling retrieve function

# Store fave num
store_txn = simple_storage.functions.store(7).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "from": my_addr,
        "chainId": chain_id,
        "nonce": nonce+1
    }
)

signed_store_txn = w3.eth.account.sign_transaction(store_txn, private_key=pk)
print("Updating favourite number....")
txn_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)

txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print("Updated favourite number:")
print(simple_storage.functions.retrieve().call())  # calling retrieve function
