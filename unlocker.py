from pymongo import MongoClient
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

sender_address = ''
sender_private_key = ''

load_config('eleneum.json')

client = MongoClient('mongodb://localhost:27017')
db = client['eleneum']
poolblocks_collection = db['poolblocks']
poolsoloblocks_collection = db['poolsoloblocks']
blocks_collection = db['blocks']
transactions_collection = db['transactions']
pool_collection = db['pool']
poolpayments_collection = db['poolpayments']
query = {"$or": [{"reward": {"$exists": False}}, {"reward": "0"}]}
poolblocks = poolblocks_collection.find(query)

pplns = 1

query = {"reward": {"$ne": "0"}}
prevhashq = poolblocks_collection.find(query).sort("ts", -1).limit(1)

z = blocks_collection.find_one(sort=[("height", -1)])
try:
    actualheight = int(z['height'])
except:
    actualheight = 1

print(actualheight)

try:
    pblock = prevhashq.next()
    previous_height = pblock['height']
except StopIteration:
    previous_height = 0
except Exception as e:
    previous_height = 0

for block in poolblocks:
    height = block['height']
    
    if actualheight - 30 < int(height):
        continue
    
    if pplns == 1:
        pplnsheight = height - 100
        if previous_height < pplnsheight:
            pplnsheight = previous_height
    else:
        pplnsheight = previous_height
    
    transaction_query = {"block": int(height), "type": 1}
    transaction = transactions_collection.find_one(transaction_query)
    
    if transaction:
        if transaction['txinfo']['sender'].lower() == sender_address.lower():
            value = transaction['txinfo']['value']
        else:
            value = -1
        poolblocks_collection.update_one({"_id": block["_id"]}, {"$set": {"reward": value}})
        print(f"Height: {height}, Value: {value} agregado a poolblocks")

    if int(value) > 0:
        pool_query = {"solo": 0, "block": {"$gt": int(pplnsheight), "$lte": int(height)}}
        pool_records = pool_collection.find(pool_query)
        address_totals = {}
        totals = 0
        payable = round(int(value) * 0.98, 4)
        for record in pool_records:
            address = record['address']
            target = record['target']
            totals += target
            if address in address_totals:
                address_totals[address] += target
            else:
                address_totals[address] = target
      
        for address, total in address_totals.items():
            btotal = total / totals
            pay = btotal * payable
            r = poolpayments_collection.insert_one( { 'address': address, 'block': height, 'value': pay, 'status': -1 } )
    #pool_collection.delete_many({"block": {"$lte": int(height)}})
    previous_height = int(height)

query = {"$or": [{"reward": {"$exists": False}}, {"reward": "0"}]}
poolsoloblocks = poolsoloblocks_collection.find(query)

print("SOLO:")
for block in poolsoloblocks:
    height = block['height']
    
    if actualheight - 30 < int(height):
        continue

    transaction_query = {"block": int(height), "type": 1}
    transaction = transactions_collection.find_one(transaction_query)

    if transaction:
        if transaction['txinfo']['sender'].lower() == sender_address.lower():
            value = transaction['txinfo']['value']
        else:
            value = -1
        poolsoloblocks_collection.update_one({"_id": block["_id"]}, {"$set": {"reward": value}})
        print(f"Height: {height}, Value: {value} agregado a poolblocks")
    
    if int(value) > 0:
        address_totals = {}
        totals = 0
        payable = round(int(value) * 0.98, 4)
        address = block['address']
        if address in address_totals:
            address_totals[address] += payable
        else:
            address_totals[address] = payable
        for address, total in address_totals.items():
            r = poolpayments_collection.insert_one( { 'address': address, 'block': height, 'value': total, 'status': -1 } )
    #pool_collection.delete_many({"block": {"$lte": int(height)}})
