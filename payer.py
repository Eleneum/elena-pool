from pymongo import MongoClient
from web3 import Web3
import rlp
from eth_typing import HexStr
from eth_utils import to_bytes
from eth_utils import to_checksum_address
from ethereum.transactions import Transaction
import requests
from datetime import datetime

w3 = Web3()

sender_address = 'SENDER_ADDRESS'
sender_private_key = 'YOUR_PRIVATE_KEY'

client = MongoClient('mongodb://localhost:27017')
db = client['eleneum']
poolpayments_collection = db['poolpayments']

filter = {'status': -1}

results = poolpayments_collection.find(filter)

address_sums = {}
for result in results:
    address = result['address']
    value = result['value']

    if address in address_sums:
        address_sums[address] += value
    else:
        address_sums[address] = value

    poolpayments_collection.update_one({'_id': result['_id']}, {'$set': {'status': 1}})


for address, sumvalue in address_sums.items():
    svalue = (sumvalue/1000000000000000000)
    print(f"Address: {address}, SumValue: {svalue}")

    print(f"Fee value: {svalue}")
    try:

        recipient_address = to_checksum_address(address)#.lower()
        value = w3.to_wei(svalue, 'ether')

        nonce = datetime.now().timestamp()
        nonce = int(nonce)

        tx = {
            'nonce': nonce,
            'to': recipient_address,
            'value': value,
            'gas': 53000,
            'gasPrice': w3.to_wei('1', 'gwei'),
            'chainId': 666999
        }

        signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
        print(str(signed_tx.rawTransaction.hex()))

        url = 'http://localhost:8080/addtransaction'
        response = requests.post(url, data=str(signed_tx.rawTransaction.hex()))
        print(response.json())
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
