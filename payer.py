from pymongo import MongoClient
from web3 import Web3
import rlp
from eth_typing import HexStr
from eth_utils import to_bytes
from eth_utils import to_checksum_address
from ethereum.transactions import Transaction
import requests
from datetime import datetime
import time
import json
from eth_account import Account

def load_config(filename):
    global sender_private_key
    global sender_address
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: File " + str(filename) + " not exists")
        exit(1)
    except json.JSONDecodeError as e:
        print("Error: File " + str(filename) + " is not valid")
        exit(1)

    if 'private_key' not in data:
        print("Error: File " + str(filename) + " does not contains any private key")
        exit(1)

    try:
        sender_private_key = data['private_key']
        sender_account = Account.from_key(sender_private_key)
        sender_address = sender_account.address
    except Exception as e:
        print("Error: File " + str(filename) + " contains an invalid private key")
        exit(1)
    
    print("Eleneum server started with address: " + sender_address)

w3 = Web3()

sender_address = ''
sender_private_key = ''

load_config('eleneum.json')

client = MongoClient('mongodb://localhost:27017')
db = client['eleneum']
poolpayments_collection = db['poolpayments']
pooltxs_collection = db['pooltransactions']
txs_collection = db['transactions']
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
    svalue = sumvalue/1000000000000000000
    print(f"Address: {address}, SumValue: {svalue}")
#    svalue -= 0.000053
    print(f"Fee value: {svalue}")
    try:
        recipient_address = to_checksum_address(address)
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
        ts = int(time.time())
        pooltxs_collection.insert_one({'timestamp': ts, 'value': str(value), 'rawtx': str(signed_tx.rawTransaction.hex())})
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)

for r in pooltxs_collection.find():
    z = txs_collection.find({'rawtx':r['rawtx']})
    if 'hash' in z:
        continue
    url = 'http://pool.eleneum.org:9090/addtransaction'
    response = requests.post(url, data=str(r['rawtx']))
    data = response.json()
    print(data)