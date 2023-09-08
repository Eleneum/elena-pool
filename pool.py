import json
import socket
import threading
import struct
import requests
from pymongo import MongoClient
import random
import time
import pyrx
import binascii
from Cryptodome.Util.number import long_to_bytes
from eth_utils import to_bytes, is_hex
from eth_typing import HexStr

open_sockets = {}
fixed_diffs = {}
extranonce_diffs = {}
extranonce_h = {}
extranonce_t = {}
miningdiff = {}
ban = {}
validation = {}
accepted = 0
rejected = 0

START_DIFF = 130000

def to_byte_array(b):
    return [byte for byte in b]

def pack_nonce(blob, nonce):
    b = binascii.unhexlify(blob)
    bin = struct.pack('39B', *bytearray(b[:39]))
    bin += struct.pack('I', nonce)
    bin += struct.pack('{}B'.format(len(b)-43), *bytearray(b[43:]))
    return bin

def compute_hash(b, n, s, h):
    seed = binascii.unhexlify(s);
    nonce = struct.unpack('I',binascii.unhexlify(n))[0]
    bin = pack_nonce(b, nonce)
    hex_hash = binascii.hexlify( pyrx.get_rx_hash(bin, seed, h) )
    return hex_hash

def hex_to_bytes(data: str) -> bytes:
    return to_bytes(hexstr=HexStr(data))

def is_eth_address(cadena):
    if len(cadena) != 42:
        return False
    if not cadena.startswith("0x"):
        return False
    direccion_hex = cadena[2:]
    return all(caracter in "0123456789abcdefABCDEF" for caracter in direccion_hex)

def get_extranonce_diff(extranonce):
    global START_DIFF
    global fixed_diffs
    global extranonce_t
    global extranonce_h

    if extranonce in fixed_diffs:
        if fixed_diffs[extranonce] >= 200000:
            return fixed_diffs[extranonce]

    if int(extranonce_h[extranonce]) > 0:
        ts = int(time.time())
        tsdiff = ts - extranonce_t[extranonce]
        diff = int(int(extranonce_h[extranonce]) / int(tsdiff))*60
    else:
        diff = START_DIFF
    return diff

def send_messages(server):

    try:
        tsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tsocket.settimeout(30)
        tsocket.connect((server, 5566))
    except Exception as e:
        print("Reloading socket")
        return
    
    try:
        global actualblock
        global accepted
        global rejected
        
        print("[worker] " + str(int(time.time())) + " ZMQ loaded")
        
        url = "http://localhost:9090/getminingtemplate"
        response = requests.get(url)
        data = response.json()
        blob = data['blob']
        height = data['height']
        diff = data['difficulty']
        seed = data["seed"]
        miningdiff["height"] = height
        miningdiff["main"] = int(data['difficulty'])
        miningdiff["blob"] = blob
        sockets = list(open_sockets.keys()) 
        miners = 0
        for sock in sockets:
            try:
                jobid = random.randint(1000, 1000000)
                job_id = jobid
                extranonce_hex = open_sockets[sock]
                diff = get_extranonce_diff(extranonce_hex)
                if diff > int(data['difficulty']):
                    diff = int(data['difficulty'])
                extranonce_diffs[extranonce_hex] = diff
                ndiff = diff
                diff = decimal_to_swapendian(diff)

                blob = extranonce_hex + blob[4:]
                        
                newjob = {"jsonrpc":"2.0","method":"job","params":{"blob":blob,"job_id":str(jobid),"target":str(diff),"height":height,"seed_hash":seed}}
                response_json = json.dumps(newjob) + "\n"
                sock.sendall(response_json.encode('utf-8'))
                miners += 1
            except:
                del open_sockets[sock]
        print("[worker] " + str(int(time.time())) + ", New job sent to: " + str(miners) + " miners")
        
        while True:
            print("conectado a socket")
            try:
                message = tsocket.recv(1024).decode('utf-8')
            except socket.timeout:
                tsocket.close()
                return
                break

            if not message:
                tsocket.close()
                return
                break
            
            message = message.rstrip()
            
            print("[worker] " + str(int(time.time())) + ", New block received: " + str(message))
            url = "http://localhost:9090/getminingtemplate"
            response = requests.get(url)
            data = response.json()
            blob = data['blob']
            height = data['height']
            diff = data['difficulty']
            seed = data["seed"]
            miningdiff["height"] = height
            miningdiff["main"] = int(data['difficulty'])
            miningdiff["blob"] = blob
            sockets = list(open_sockets.keys()) 
            miners = 0
            for sock in sockets:
                try:
                    jobid = random.randint(1000, 1000000)
                    job_id = jobid
                    extranonce_hex = open_sockets[sock]
                    diff = get_extranonce_diff(extranonce_hex)
                    if diff > int(data['difficulty']):
                        diff = int(data['difficulty'])
                    extranonce_diffs[extranonce_hex] = diff
                    ndiff = diff
                    diff = decimal_to_swapendian(diff)

                    blob = extranonce_hex + blob[4:]
                        
                    newjob = {"jsonrpc":"2.0","method":"job","params":{"blob":blob,"job_id":str(jobid),"target":str(diff),"height":height,"seed_hash":seed}}
                    response_json = json.dumps(newjob) + "\n"
                    sock.sendall(response_json.encode('utf-8'))
                    miners += 1
                except:
                    del open_sockets[sock]
                        
            print("[worker] " + str(int(time.time())) + ", New job sent to: " + str(miners) + " miners")
            print("[worker] " + str(int(time.time())) + ", Banned IP's: " + str(len(ban)))
            print("[worker] " + str(int(time.time())) + ", On last block, Accepted shares: " + str(accepted) + ", Rejected shares: " + str(rejected))
            rejected = 0
            accepted = 0
        return
    except Exception as e:
        print("Closing socket")
        tsocket.close()
        return

def decimal_to_swapendian(decimal_value):
    result = 0
    if decimal_value != 0:
        result = 0x100000001 / decimal_value
    hex_value = hex(int(result))[2:].zfill(8)
    swapped = hex_value[6:] + hex_value[4:6] + hex_value[2:4] + hex_value[:2]
    return swapped

base_diff = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

def handle_connection(conn, addr):
    global ban
    global START_DIFF
    global validation
    global accepted
    global rejected
    global extranonce_diffs
    global extranonce_h
    global extranonce_t
    global fixed_diffs

    dbmongo = 'mongodb://127.0.0.1:27017'
    client = MongoClient(dbmongo)
    bcdb = client["eleneum"]
    pool = bcdb["pool"]
    poolblocks = bcdb["poolblocks"]
    poolsoloblocks = bcdb["poolsoloblocks"]
    poolworkers = bcdb["poolworkers"]
    jobid = 1
    address = None
    diff = 0
    tpass = ""
    vaddr = str(addr[0])

    if addr[0] not in ban:
        ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
    else:
        ban[addr[0]]["attempts"] += 1

    if vaddr not in validation:
        validation[vaddr] = 0

    while True:
        extranonce = random.randint(0, 2**32-1)
        extranonce_hex = hex(extranonce)[2:]  # Convierte el número a hexadecimal y elimina los primeros dos caracteres
        extranonce_hex = extranonce_hex[0:4]
        if extranonce_hex not in extranonce_diffs:
            break

    extranonce_diffs[extranonce_hex] = 0
    extranonce_h[extranonce_hex] = 0
    extranonce_t[extranonce_hex] = int(time.time())

    timeout_seconds = 300

    while True:
        newjob = None

        conn.settimeout(timeout_seconds)
        try:
            data = conn.recv(1024).decode('utf-8')
            data = data.rstrip()
        except socket.timeout:
            conn.close()
            return

        if not data:
            conn.close()
            if int(extranonce_h[extranonce_hex]) == 0:
                if addr[0] not in ban:
                    ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
                else:
                    ts = int(time.time())
                    if int(ban[addr[0]]["timestamp"]) + 600 > ts:
                        ban[addr[0]]["attempts"] += 1
                    else:
                        ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
            return

        else:
            response = None
            try:
                request = json.loads(data)
                if request["method"] == 'submit':
                    params = request["params"]
                    hex_hash = params['result']
                    hash_bytes = bytes.fromhex(hex_hash)
                    hash_array = to_byte_array(hash_bytes)[::-1]
                    hash_num = int.from_bytes(bytes(hash_array), byteorder='big')
                    hash_diff = base_diff / hash_num
                    nonce = params["nonce"]
                    mnonce = params["nonce"]
                    nonce = extranonce_hex + nonce
                    targetdiff = int(extranonce_diffs[extranonce_hex])
                    extranonce_h[extranonce_hex] += targetdiff

                    response = {"jsonrpc":"2.0","id":request["id"],"result":{"status":"ok"}}

                    if hash_diff >= miningdiff["main"]:
                        url = 'http://localhost:9090/mineblock'
                        nresponse = requests.post(url, data=nonce)
                        json_data = nresponse.json()
                        if json_data["status"] == "ok":
                            accepted += 1
                            print("[miner0] " + str(int(time.time())) + ", Block mined. Height: " + json_data["height"] + ", diff: " + json_data["difficulty"])
                            json_data['ts'] = time.time()
                            json_data['height'] = int(json_data['height'])
                            json_data['reward'] = "0"
                            json_data['address'] = address
                            if tpass != "solo":
                                rpb = poolblocks.insert_one( json_data )
                                r = pool.insert_one( { 'extranonce': extranonce_hex, 'address': address, 'target': targetdiff, 'difficulty': hash_diff, 'block': miningdiff["height"], 'nonce': mnonce, 'ts': time.time(), 'mined' : 1, 'solo' : 0  } )
                            else:
                                rpb = poolsoloblocks.insert_one( json_data )
                                r = pool.insert_one( { 'extranonce': extranonce_hex, 'address': address, 'target': targetdiff, 'difficulty': hash_diff, 'block': miningdiff["height"], 'nonce': mnonce, 'ts': time.time(), 'mined' : 1, 'solo' : 1   } )
                        else:
                            rejected += 1
                            response = {"jsonrpc":"2.0","id":request["id"],"result":{"status":"rejected"}}
                    elif hash_diff > targetdiff:
                        if tpass == "solo":
                            r = pool.insert_one( { 'extranonce': extranonce_hex, 'address': address, 'target': targetdiff, 'difficulty': hash_diff, 'block': miningdiff["height"], 'nonce': mnonce, 'ts': time.time(), 'mined' : 0, 'solo' : 1 } )
                        else:
                            if validation[vaddr] < 5:
                                seed = "0000000000000000000000000000000000000000000000000000000000000313"
                                blob = extranonce_hex + miningdiff["blob"][4:]
                                mhex_hash = compute_hash(blob, mnonce, seed, miningdiff["height"])
                                mhash_bytes = bytes.fromhex(mhex_hash.decode())
                                mhash_array = to_byte_array(mhash_bytes)[::-1]
                                mhash_num = int.from_bytes(bytes(mhash_array), byteorder='big')
                                hash_diff = base_diff / mhash_num
                                if hash_diff >= targetdiff:
                                    accepted += 1
                                    validation[vaddr] += 1
                                    r = pool.insert_one( { 'extranonce': extranonce_hex, 'address': address, 'target': targetdiff, 'difficulty': hash_diff, 'block': miningdiff["height"], 'nonce': mnonce, 'ts': time.time(), 'mined' : 0, 'solo' : 0  } )
                                else:
                                    rejected += 1
                                    validation[vaddr] -= 1
                                    response = {"jsonrpc":"2.0","id":request["id"],"result":{"status":"rejected"}}
                                    if validation[vaddr] < -5:
                                        ban[addr[0]] = { "attempts": 20, "timestamp": int(time.time()) }
                                        response_json = json.dumps(response) + "\n"
                                        conn.send(response_json.encode('utf-8'))
                                        return
                            else:
                                accepted += 1
                                r = pool.insert_one( { 'extranonce': extranonce_hex, 'address': address, 'target': targetdiff, 'difficulty': hash_diff, 'block': miningdiff["height"], 'nonce': mnonce, 'ts': time.time(), 'mined' : 0, 'solo' : 0  } )
                elif request["method"] == 'login':
                    params = request["params"]
                    agent = params["agent"].lower()

                    if "xmr" not in agent:
                        response = { "id": request["id"], "error": {"code" : -6,  "message": "Invalid miner" } }
                        ban[addr[0]] = { "attempts": 20, "timestamp": int(time.time()) }
                        response_json = json.dumps(response) + "\n"
                        conn.send(response_json.encode('utf-8'))
                        conn.close()
                        return

                    fixed_diff = 0
                    address = params["login"].lower()

                    if ":" in address:
                        address_parts = address.split(":")
                        wallet_address = address_parts[0]
                        fixed_diff = int(address_parts[1])
                    else:
                        wallet_address = address

                    address = wallet_address

                    if "." in address:
                        address_parts = address.split(".")
                        wallet_address = address_parts[0]
                        workerid = address_parts[1]
                    else:
                        wallet_address = address
                        workerid = ""

                    address = wallet_address

                    if fixed_diff >= 200000:
                        fixed_diffs[extranonce_hex] = int(fixed_diff)

                    if is_eth_address(address) == True:
                        open_sockets[conn] = extranonce_hex
                        tpass = params["pass"]
                        r = poolworkers.insert_one( { 'address': address, 'workerid': workerid, 'extranonce': extranonce_hex } )
                        print("[miner0] " + str(int(time.time())) + ", Miner connected: " + str(address) + " from " + str(addr))
                        if addr[0] in ban:
                            ban[addr[0]]["attempts"] -= 1

                        url = "http://localhost:9090/getminingtemplate"
                        nresponse = requests.get(url)
                        data = nresponse.json()
                        if int(data['difficulty']) < START_DIFF:
                            diff = decimal_to_swapendian(int(data['difficulty']))
                            extranonce_diffs[extranonce_hex] = int(data['difficulty'])
                        else:
                            diff = decimal_to_swapendian(START_DIFF)
                            extranonce_diffs[extranonce_hex] = START_DIFF
                        miningdiff["main"] = int(data['difficulty'])
                        targetdiff = int(extranonce_diffs[extranonce_hex])
                        job_id = '42'
                        blob = data['blob']
                        blob = extranonce_hex + blob[4:]
                        height = data['height']
                        seed = data["seed"]

                        if fixed_diff >= 200000:
                            diff = decimal_to_swapendian(fixed_diff)

                        response = {"jsonrpc":"2.0","id":request["id"],"result":{"id":str(jobid),"job":{"blob":blob,"job_id":"2951","target":str(diff),"height":height,"seed_hash":seed},"status":"OK"}}
                        jobid = jobid + 1
                    else:
                        response = { "id": request["id"], "error": {"code" : -6,  "message": "Invalid wallet address" } }
                        conn.close()
                        return
                else:
                    print("no se que quieres")
                    ban[addr[0]]["attempts"] += 1
                    conn.close()
                    return
            except ValueError as e:
                response = {"id": None, "error": {"code": -32700, "message": "Parse error"}}
                if addr[0] not in ban:
                    ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
                else:
                    ts = int(time.time())
                    if int(ban[addr[0]]["timestamp"]) + 600 > ts:
                        ban[addr[0]]["attempts"] += 1
                    else:
                        ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
                conn.close()
                return
            except Exception as e:
                response = {"id": None, "error": {"code": -32603, "message": "Internal error"}}
                response_json = json.dumps(response) + "\n"
                if addr[0] not in ban:
                    ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
                else:
                    ts = int(time.time())
                    if int(ban[addr[0]]["timestamp"]) + 600 > ts:
                        ban[addr[0]]["attempts"] += 1
                    else:
                        ban[addr[0]] = { "attempts": 1, "timestamp": int(time.time()) }
                conn.close()
                return
            if response is not None:
                response_json = json.dumps(response) + "\n"
                conn.send(response_json.encode('utf-8'))
            
            if addr[0] in ban:
                ts = int(time.time())
                if int(ban[addr[0]]["timestamp"]) + 600 > ts and int(ban[addr[0]]["attempts"]) >= 5:
                    conn.close()
                    return
                else:
                    if int(ban[addr[0]]["timestamp"]) + 600 < ts and int(ban[addr[0]]["attempts"]) >= 5:
                        del ban[addr[0]] 

def mining():
    global ban
    port = 3355
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(50)
    print(f'Mining on port {port}')

    at = 0

    while True:
        conn, addr = s.accept()
        if addr[0] in ban:
            ts = int(time.time())
            if int(ban[addr[0]]["attempts"]) < 5 or int(ban[addr[0]]["timestamp"]) + 600 < ts:
                if int(ban[addr[0]]["timestamp"]) + 600 < ts and int(ban[addr[0]]["attempts"]) >= 5:
                    del ban[addr[0]]
                at += 1
                print("ts: " + str(at))
                t = threading.Thread(target=handle_connection, args=(conn, addr))
                t.start()
            else:
                #print("IP " + str(addr[0]) + " is banned for 10 minutes. Remaining in secs: " + str(int(ban[addr[0]]["timestamp"]) + 600 - ts))
                conn.close()
        else:
            at += 1
            print("ts: " + str(at))
            t = threading.Thread(target=handle_connection, args=(conn, addr))
            t.start()

def poolstart():
    x = threading.Thread(target=mining, args=())
    x.start()

    send_thread = threading.Thread(target=send_messages, args=("localhost",))
    send_thread.start()

    while True:
        if not send_thread.is_alive():
            send_thread = threading.Thread(target=send_messages, args=("localhost",))
            send_thread.start()
        time.sleep(1)

poolstart()
