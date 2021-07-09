import os, configparser, json
from web3 import Web3
import re

path = os.path.abspath('.')
cfgpath = path.split('BIM_P_API')[0] + 'BIM_P_API/config.ini'
config = configparser.ConfigParser()
config.read(cfgpath)

def Transaction(mqtt_data, S_Blkchain_ID):
    w3 = Web3(Web3.HTTPProvider("http://" + config['ETHEREUM']['host'] + ":" + config['ETHEREUM']['port']))
    w3.parity.personal.unlockAccount(w3.toChecksumAddress(config['ETHEREUM']['miner_account']), config['ETHEREUM']['miner_passwd'], 0)

    input_json = json.dumps(mqtt_data)

    input_data = bytes(input_json, encoding = "utf8")
    # print(type(mqtt_data))
    tx = w3.eth.sendTransaction({
        'to': w3.toChecksumAddress(str(S_Blkchain_ID)),
        'from': w3.eth.coinbase,
        'value': 1000,
        'data': input_data
    })

    # ------------------------------------------------------------------------------------------------------ #
    #print("Original hashbyte:",tx)
    #print("\n")
    
    #convert sendtransaction to hex
    tx1 = tx.hex()

    test = bytes.fromhex(tx1[2:])
    #print(test)
    #print transaction hash
    #print("hex:",tx1)
    #print("\n")
    # print("transaction time:",total_time.seconds+total_time.microseconds/1000000)

    #get transaction hash
    get_input_hash = w3.eth.getTransaction(test)
    #transaction detail
    #print("transaction detail:", get_input_hash)
    #print("\n")
    #get transaction input
    #print("Original input hash:", get_input_hash['input'])
    #print("\n")
    get_input = get_input_hash['input']
    #conver input hex to string & delete 0x
    get_input = get_input[2:]
    #print(get_input)
    input_result = bytes.fromhex(get_input).decode('utf-8')
    #print("decode input:",input_result)
    #print("\n")

    return str(tx1)

def Verification(hashcode): 
    w3 = Web3(Web3.HTTPProvider("http://" + config['ETHEREUM']['host'] + ":" + config['ETHEREUM']['port']))
    w3.parity.personal.unlockAccount(w3.toChecksumAddress(config['ETHEREUM']['miner_account']), config['ETHEREUM']['miner_passwd'], 0)

    test = bytes.fromhex(hashcode[2:])
    # print(test)
    get_input_hash = w3.eth.getTransaction(test)
    get_input = get_input_hash['input']
    get_input = get_input[2:]
    input_result = bytes.fromhex(get_input).decode('utf-8')

    input_result = input_result.replace('\\','')
    input_result = input_result.replace('\"', '\'')
    #input_result = bytes.fromhex(get_input)

    #print(input_result)

    return input_result

