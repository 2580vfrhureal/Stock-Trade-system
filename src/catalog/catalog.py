import json
import threading
from time import sleep
from flask import Flask, request
import requests

app = Flask(__name__)
catalog = []  # memory stored from the disk
lock = threading.Lock()  # lock for memory database
disk_lock = threading.Lock()  # lock for disk database


# notify front end server which stock be updated
def update_cache(stock_name):
    requests.get('http://0.0.0.0:xxxx/rm?stock_name=%s'%stock_name) # port tbd

# initial database
def init_database():
    with open('catalog.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            info = line.split(' ')
            item = {
                'stock_name': info[0],
                'price': float(info[1]),
                'trade_volume':int(info[2]),
                'quantity': int(info[2])
            }
            catalog.append(item)
    f.close()

# write in file
def write():
    global catalog
    data = ''
    for item in catalog:
        data += '%s %s %s %s\n' % (item['name'], item['price'],item['trade_volume'],item['quantity'])
    # lock file in disk
    with disk_lock:
        f = open('catalog.txt', 'w')
        f.write(data)
        f.close()


# query stock info
@app.route('/query', methods=['GET'])
def products():
    global catalog
    stock_name = request.args.get('stock_name')
    print(stock_name)
    with lock:
        for item in catalog:
            # if found target stock in database
            if item['stock_name'] == stock_name:
                js = json.dumps({'data': item})
                return js
        # if not find the toy
        # send back product not found error
        js = json.dumps(
            {'error': {
                'code': 404,
                'message': 'product not found'
            }})
        return js, 404


# buy/sell stock
@app.route('/trade', methods=['POST'])
def buy():
    data = request.data
    data = str(data, 'utf-8')
    data = eval(data)
    print(data)
    stock_name,quantity = data['stock_name'],data['quantity']
    print('name: %s, quantity: %s' % (stock_name, quantity))
    with lock:
        for item in catalog:
            if item['name'] == stock_name:
                if item['quantity'] - int(quantity) >= 0:
                    item['quantity'] -= int(quantity)
                    js = json.dumps({'message': 'order has been placed'})
                    write()
                    # notify frontend
                    update_cache(stock_name)
                    return js
                else:
                    js = json.dumps({'message': 'out of stock'})
                    return js, 404
        js = json.dumps({'message': 'stock not found'})
        return js, 404

if __name__ == '__main__':
    port=10086
    init_database()
    print(catalog)
    
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
