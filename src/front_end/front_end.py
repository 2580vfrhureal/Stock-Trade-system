import json
import os
import threading
from time import sleep
from flask import Flask, request
import requests

front_server = Flask(__name__)
stock_cache = []
lock = threading.Lock()  # file lock

# get the ip address of catalog server and order server from env var
# defult with 'catalog' and 'order'
# since in docker-compose they are in special network which can communicate by host name
catalog_server_addr = os.getenv('CATALOG', 'catalog')
leader_server = os.getenv('ORDER', 'order')


# check cache
def isExist(stock_name):
    for item in stock_cache:
        if item['stock_name'] == stock_name:
            return True
    return False


# append cache
def add(item):
    with lock:
        item = json.loads(item)
        stock_cache.append(item)

# remove cache API
# response for the requests from catalog server
@front_server.route('/rm', methods=['GET'])
def rm():
    stock_name = request.args.get('stock_name')
    if isExist(stock_name):
        with lock:
            for item in stock_cache:
                if item['stock_name'] == stock_name:
                    stock_cache.remove(item)
                    return 'removed successfully'


# query stocks
@front_server.route('/stocks', methods=['GET'])
def products():
    stock_name = request.args.get('stock_name')
    print(stock_name)
    # if exist in cache
    if isExist(stock_name):
        for item in stock_cache:
            if item['name'] == stock_name:
                res = json.dumps(item)
                print('sent from cache')
                return res
    # if not in cache
    else:
        try:
            # send query request to catalog server
            r = requests.get('http://0.0.0.0:10001/query?stock_name=%s' % stock_name)
            res = res.json()
            if r.status_code == 200:
                print(res['data']['stock_name'],
                    res['data']['price'],
                    res['data']['trade_volume'],
                    res['data']['quantity'],
                    flush=True)
                re = json.dumps({
                    "name": res['data']['stock_name'],
                    'price': res['data']['price'],
                    'trade_volume': res['data']['trade_volume'],
                    'quantity': res['data']['quantity']
                })
                add(re) # add item into cache
                return re
            elif r.status_code == 404:
                re = json.dumps(res)
                return re, 404
            else:
                return 'unexpected error'
        except:
            return 'unknown error'
        
# order service
@front_server.route('/orders', methods=['POST', 'GET'])
def orders():
    if request.method == 'GET':
        order_no = request.args.get('order_no')
        print(order_no)
        r = requests.get('http://0.0.0.0:%s/query?order_no=%s' % (leader_server,order_no))
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return r.json()
        else:
            return 'unexpected error'
    elif request.method == 'POST':
        data = request.get_json()
        # data = json.loads(data)
        print(data)
        stock_name,trade_type,quantity = data['stock_name'],data['trade_type'],data['quantity']
        r = requests.get(
            'http://0.0.0.0:%s/orders?toyname=%s&&trade_type=%s&&quantity=%s' %
            (leader_server,stock_name, trade_type,quantity))
        return r.json()
        
# return leader id
@front_server.route('/leader',methods=['GET'])
def leader():
    return json.dumps({'leader':leader_server})

# leader election
def ping():
    while True:
        try:
            requests.get('http://0.0.0.0:%s/ping'%leader_server)
        except Exception as e:
            leader_election()
        sleep(5)
    
    

def leader_election():
    order_servers= ['20001', '20002', '20003']
    alive_servers=[]
    # ask each order server 
    for order in order_servers:
        try:
            # if the order server alive,return the order server ID
            r=requests.get('http://0.0.0.0:%s/ping'%order)
            alive_servers.append({'id':r.json()['alive order server'],'port':order})
        except Exception as e:
            print('%s failed!'%order)
    
    alive_servers=sorted(alive_servers,key=lambda x: x['id']) # sort by id
    global leader_server

    
    # set leader's port
    leader_server = alive_servers[-1]['port']
    for order in order_servers:
        try:
            # notify each order server
            r=requests.get('http://0.0.0.0:%s/leader?leader=%s'%(order,leader_server))
        except Exception as e:
            print('%s failed!'%order)

if __name__ == '__main__':
    port=30001
    leader_election()
    print('now leader is %s'%leader_server)
    threading.Thread(target=ping).start()
    front_server.run(host='0.0.0.0', port=port, debug=True, threaded=True)
