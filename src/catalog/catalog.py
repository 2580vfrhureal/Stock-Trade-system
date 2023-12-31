import json
import threading
from time import sleep
from flask import Flask, request
import requests
import os

catalog_server = Flask(__name__)
catalog_db = []  # catalog db
lock = threading.Lock()  # lock for dic db
disk_lock = threading.Lock()  # lock for disk db
ip_addr = os.getenv("CATALOG", "0.0.0.0")

# initial database
def init_database():
    with open('catalog.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            s = line.split(' ')
            item = {
                'stock_name': s[0],
                'price': float(s[1]),
                'trade_volume':int(s[2]),
                'quantity': int(s[3])
            }
            catalog_db.append(item)
    f.close()

# write in file
def write():
    global catalog_db
    data = ''
    for item in catalog_db:
        data += '%s %s %s %s\n' % (item['stock_name'], item['price'],item['trade_volume'],item['quantity'])
    # lock file in disk
    with disk_lock:
        f = open('catalog.txt', 'w')
        f.write(data)
        f.close()


# query stock info
@catalog_server.route('/query', methods=['GET'])
def products():
    global catalog_db
    stock_name = request.args.get('stock_name')
    print(stock_name)
    with lock:
        for item in catalog_db:
            # if found target stock in database
            if item['stock_name'] == stock_name:
                res = json.dumps({'data': item})
                print(res)
                print("sending query result back")
                return res
        # response 404
        res = json.dumps(
            {'error': {
                'code': 404,
                'message': 'Stock not found'
            }})
        return res, 404


# buy/sell stock
@catalog_server.route('/trade', methods=['POST'])
def buy():
    # data = request.get_json()
    # data = json.loads(data)
    data = request.data
    data = str(data, 'utf-8')
    data = eval(data)
    print(data)
    stock_name,trade_type,quantity = data['stock_name'],data['type'],data['quantity']
    print('name: %s,type: %s, quantity: %s' % (stock_name,trade_type,quantity))
    with lock:
        for item in catalog_db:
            if item['stock_name'] == stock_name:
                if str(trade_type) == "Sell" and item['quantity'] + int(quantity) <= 100:
                    item['quantity'] += int(quantity)
                    item['trade_volume'] += int(quantity)
                    print("sell successfully")
                    res = json.dumps({'message':'order had been trade successfully!'})
                    write()
                    update_cache(stock_name)
                    return res
                elif str(trade_type) == "Buy" and item['quantity'] - int(quantity) >= 0:
                    item["quantity"] -= int(quantity)
                    item['trade_volume'] += int(quantity)
                    print(catalog_db)
                    print("buy successfully")
                    res = json.dumps({'message':'order had been trade successfully!'})
                    write()
                    update_cache(stock_name)
                    return res
                else:
                    res = json.dumps({'message':'Trade failed!'})
                    return res,404
            
        res = json.dumps({'message':'Stock not found!'})
        return res,404

# notify front end server which stock be updated
def update_cache(stock_name):
    requests.get('http://%s:30001/rm?stock_name=%s'%(ip_addr,stock_name)) # port tbd
    print("sent update cache request")

if __name__ == '__main__': #ensure this module implement as main module
    port=10001
    init_database()
    print(catalog_db)

    catalog_server.run(host=ip_addr, port=port, debug=True, threaded=True)
