import json
import os
import threading
from time import sleep
from flask import Flask, request
import requests

front_server = Flask(__name__)
stock_cache = []
lock = threading.Lock()  # file lock
leader_server = os.getenv('ORDER', '20003') #port
ip_addr = os.getenv("IP", "0.0.0.0")
port=30001

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
    print(stock_cache)
    stock_name = request.args.get('stock_name')
    print("removing %s" % stock_name)
    if isExist(stock_name):
        with lock:
            i = 0
            for item in stock_cache:
                if item['stock_name'] == stock_name:
                    stock_cache.remove(item)
                    print("removed successfully")
                    print(stock_cache)
                    res = json.dumps({
                        "stock_name": stock_name,
                        "message": "removed successfully"
                    })
                    return res
                i+=1
    res = json.dumps({
        "message": "this stock isn't exist in cache"
    })
    return res


# query stocks
@front_server.route('/stocks', methods=['GET'])
def products():
    stock_name = request.args.get('stock_name')
    print(stock_name)
    # if exist in cache
    if isExist(stock_name):
        for item in stock_cache:
            if item['stock_name'] == stock_name:
                res = json.dumps(item)
                print('sent from cache')
                return res
    # if not in cache
    else:
        try:
            # send query request to catalog server
            print("sent query to catalog server")
            r = requests.get('http://%s:10001/query?stock_name=%s' % (ip_addr,stock_name))
            # res = r.json()
            res = json.loads(r.text)
            print(res)
            if r.status_code == 200:
                print(res['data']['stock_name'],
                    res['data']['price'],
                    res['data']['trade_volume'],
                    res['data']['quantity'],
                    flush=True)
                re = json.dumps({
                    'stock_name': res['data']['stock_name'],
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
        r = requests.get('http://%s:%s/query?order_no=%s' % (ip_addr,leader_server,order_no))
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return r.json()
        else:
            return 'unexpected error'
    elif request.method == 'POST':
        # data = request.get_json()
        # data = json.loads(data)
        data = request.data
        data = str(data, 'utf-8')
        data = eval(data)
        print(data)
        stock_name,trade_type,quantity = data['stock_name'],data['trade_type'],data['quantity']
        r = requests.get(
            'http://%s:%s/trade?stock_name=%s&trade_type=%s&quantity=%s' %
            (ip_addr,leader_server,stock_name,trade_type,quantity))
        return r.json()
        
# return leader id
@front_server.route('/leader',methods=['GET'])
def leader():
    return json.dumps({'leader':leader_server})

# leader election
def ping():
    while True:
        try:
            requests.get('http://%s:%s/ping'%(ip_addr,leader_server))
            
        except Exception as e:
            leader_election()
        sleep(5) # waiting elect a new leader
        print('now leader is %s'%leader_server)
    
    

def leader_election():
    order_servers= ['20001', '20002', '20003']
    alive_servers=[]
    # ask each order server 
    for order in order_servers:
        try:
            # if the order server alive,return the order server ID
            r=requests.get('http://%s:%s/ping'%(ip_addr,order))
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
            r=requests.get('http://%s:%s/leader?leader=%s'%(ip_addr,order,leader_server))
        except Exception as e:
            print('%s failed!'%order)

@front_server.route('/',methods=['GET'])
def hello():
    return 'hello world'


if __name__ == '__main__':
    
    #leader_election()
    print('now leader is %s'%leader_server)
    #threading.Thread(target=ping).start()
    front_server.run(host=ip_addr, port=port, debug=True, threaded=True)
