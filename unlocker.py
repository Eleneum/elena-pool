from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017')
db = client['eleneum']  # Nombre de tu base de datos
poolblocks_collection = db['poolblocks']  # Nombre de tu colección "poolblocks"
poolsoloblocks_collection = db['poolsoloblocks']  # Nombre de tu colección "poolblocks"
info_collection = db['info']  # Nombre de tu colección "poolblocks"
transactions_collection = db['transactions']  # Nombre de tu colección "transactions"
pool_collection = db['pool']  # Nombre de tu colección "pool"
poolpayments_collection = db['poolpayments']

query = {"$or": [{"reward": {"$exists": False}}, {"reward": "0"}]}
poolblocks = poolblocks_collection.find(query)

pplns = 1

num_records = transactions_collection.count_documents({})
info_query = {"info": "totaltx"}
info_update = {"$set": {"value": num_records}}
info_collection.update_one(info_query, info_update, upsert=True)

# Prev height
query = {"reward": {"$ne": "0"}}
prevhashq = poolblocks_collection.find(query).sort("ts", -1).limit(1)

try:
    pblock = prevhashq.next()
    previous_height = pblock['height']
except StopIteration:
    previous_height = 0
except Exception as e:
    previous_height = 0

for block in poolblocks:
    height = block['height']
    if pplns == 1:
        pplnsheight = height - 50
        if previous_height < pplnsheight:
            pplnsheight = previous_height
    else:
        pplnsheight = previous_height
    
    transaction_query = {"block": int(height), "type": 1}
    transaction = transactions_collection.find_one(transaction_query)
    
    if transaction:
        value = transaction['txinfo']['value']
        poolblocks_collection.update_one({"_id": block["_id"]}, {"$set": {"reward": value}})
        print(f"Height: {height}, Value: {value} agregado a poolblocks")

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
        if address not in bwallets:
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
    
    transaction_query = {"block": int(height), "type": 1}
    transaction = transactions_collection.find_one(transaction_query)
    
    if transaction:
        value = transaction['txinfo']['value']
        poolsoloblocks_collection.update_one({"_id": block["_id"]}, {"$set": {"reward": value}})
        print(f"Height: {height}, Value: {value} agregado a poolblocks")

    address_totals = {}
    totals = 0

    payable = round(int(value) * 0.98, 4)
    fee = round(int(value) * 0.12, 4)
    
    address_totals["0x2d108a8b4da1ad960dd39836e2a8a4330695a855"] = fee
    address = block['address']
    if address in address_totals:
        address_totals[address] += payable
    else:
        address_totals[address] = payable
  
    for address, total in address_totals.items():
        #print(f"Address: {address}, Total: {total}, Total pct: {btotal}, Paid: {total}")
        r = poolpayments_collection.insert_one( { 'address': address, 'block': height, 'value': total, 'status': -1 } )
    #r = poolpayments_collection.insert_one( { 'address': "", 'block': 100000000000+int(height), 'value': fee, 'status': -1 } )
    #pool_collection.delete_many({"block": {"$lte": int(height)}})
