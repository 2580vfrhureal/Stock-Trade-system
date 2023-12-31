import json
import os
import threading
from flask import Flask, request
import requests
from shutil import copyfile

order_server = Flask(__name__)
lock = threading.Lock()  # file lock
order_db = []  # order db
order_ports = ['20001', '20002', '20003'] #
leader_id = '-1' # initial leader id
ip_addr = os.getenv("ORDER", "0.0.0.0")


# order record generator
class order_log:

    def __init__(self):
        self.value = self.init()
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.value += 1
            order_no = self.value
            return order_no

    def init(self):
        # if oder_log file exist
        if os.path.exists('order_log%s.txt' % id):
            with lock:
                f = open('order_log%s.txt' % id, 'r')
                lines = f.readlines()

                # find the latest successful trade order no
                for line in reversed(lines):
                    if int(line.split(' ')[0]) > 0:
                        return int(line.split(' ')[0])
                return 0
        else:
            return 0


# query order
@order_server.route("/query", methods=['GET'])
def query():
    order_no = request.args.get('order_no')
    print(order_no)
    for item in order_db:
        if item['order_no'] == int(order_no):
            print(item)
            res = json.dumps({
                'data': {
                    'order_no': item['order_no'],
                    'stock_name': item['stock_name'],
                    'trade_type': item['trade_type'],
                    'quantity': item['quantity']
                }
            })
            return res
    res = json.dumps({'error': {'code': 404, 'message': 'order not found'}})
    return res, 404
    

@order_server.route("/test",methods=["GET"])
def test():
    stock_name = 'Stock1'
    r = requests.get('http://%s:10001/query?stock_name=%s' % (ip_addr,stock_name))
    res = r.json()
    re = json.dumps({
        "name": res['data']['stock_name'],
        'price': res['data']['price'],
        'trade_volume': res['data']['trade_volume'],
        'quantity': res['data']['quantity']
    })
    return re

@order_server.route('/test1',methods=["GET"])
def test1():
    res = json.dumps({'connection': {'code': 200, 'message': 'order_server is working'}})
    return res,200

# process order
@order_server.route("/trade", methods=['GET'])
def orders():
    stock_name = request.args.get('stock_name')
    trade_type = request.args.get('trade_type')
    quantity = request.args.get('quantity')
    # stock_name = 'Stock1'
    # trade_type ='Buy'
    # quantity = 4
    data = json.dumps({'stock_name': stock_name, 'type':trade_type, 'quantity': quantity})
    print(data)
    r = requests.post(url='http://%s:10001/trade' %ip_addr, data=data)
    print(r)
    if r.status_code == 200:
        order_no = id_gen.increment()
        res = json.dumps({"order_no": order_no})
        with lock:
            order_db.append({
                'order_no': order_no,
                'stock_name': stock_name,
                'trade_type': trade_type,
                'quantity': quantity
            })
            f = open('order_log%s.txt' % id, 'a+') # add record
            s = '{} {} {} {}\n'.format(order_no,stock_name,trade_type,quantity)
            f.write(s)
            f.close()
        order_info = json.dumps({
            'order_no': order_no,
            'stock_name': stock_name,
            'trade_type': trade_type,
            'quantity': quantity
        })
        # once order number is generated, notify other order nodes
        sync(order_info)
        return res
    elif r.status_code == 404:
        order_no = -1
        res = json.dumps({
            "order_no": order_no,
            'message': r.json()['message']
        })
        return res, 404
    else:
        return 'Unknown Error%s' % r.status_code


# sync order log with the leader node
@order_server.route('/sync', methods=['POST'])
def sync_log():
    data = request.data
    data = str(data, 'utf-8')
    data = eval(data)
    print(data)
    order_no, stock_name, trade_type,quantity = data['order_no'], data['stock_name'], data['trade_type'],data['quantity']
    # if the order is success, increase id stored in memory by one
    # in order to consistent order num with leader
    # if order_no!=-1:
    id_gen.increment()
    # store in memory and write in log
    with lock:
        order_db.append({
            'order_no':order_no,
            'stock_name': stock_name,
            'trade_type': trade_type,
            'quantity': quantity
        })
        f = open('order_log%s.txt' % id, 'a+')
        s = '{} {} {} {}\n'.format(order_no,stock_name,trade_type,quantity)
        f.write(s)
        f.close()
    return ''
    


# spread order info to non-leader nodes
def sync(data):
    i = 1
    for order in order_ports:
        # just notify the 2 other order servers to sync order records
        if i != id:
            try:
                requests.post('http://%s:%s/sync' % (ip_addr,order),data=data)
                print("sent order log sync requests")
            except Exception:
                print('%s sync failed!' % order)
        i += 1

# when leader is selected
@order_server.route('/leader', methods=['GET'])
def leader():
    global leader_id
    leader_id = request.args.get('leader')
    return json.dumps({'message': 'received leader id'})


# ping API
@order_server.route('/ping', methods=['GET'])
def ping():
    res = json.dumps({'alive order server': id,
                      'port':port})
    return res


# read exist order info in disk before starting server
def init_order():
    # if oder_log file exist
    if os.path.exists('order_log%s.txt' % id):
        with open('order_log%s.txt' % id, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip('\n')
                info = line.split(' ')
                item = {
                    'order_no': info[0],
                    'stock_name': info[1],
                    'trade_type': info[2],
                    'quantity': info[3]
                }
                order_db.append(item)
        f.close()
        return len(order_db)
    else:
        return 0

# replica order_log from other nodes
def sync_log():
    # find latest modified .txt as source file
    exist_logs = []
    timestamps = []
    latest_file = ''
    for i in range(1,4):
        if os.path.exists('order_log%s.txt' % i):
            exist_logs.append('order_log%s.txt' % i)

    if len(exist_logs) != 0:
        for file in exist_logs:
            modified_time = os.path.getmtime(file)
            file_time = {'file_name': str(file),
                        'latest_modified':modified_time}
            timestamps.append(file_time)
            print(timestamps)
            timestamps = sorted(timestamps,key=lambda x: x['latest_modified']) 
            latest_file = timestamps[-1]['file_name']
            print("latest modified file is %s" % latest_file)
        if latest_file != str("order_log%s.txt" %str(id)):
            copyfile("%s" % latest_file, "order_log%s.txt" %str(id) ) # sync data with latest active order server
            print("replicate successfully")

def miss_orders(pre_amount):
    print("missed orders:\n")
    for item in order_db:
        if int(item['order_no']) > int(pre_amount):
            print('{} {} {} {}\n'.format(
                item['order_no'],item['stock_name'],item['trade_type'],item['quantity']))

if __name__ == '__main__':
    id = int(os.getenv('ID', 1))
    port = os.getenv('PORT', 20001)
    port = int(port)
    id_gen = order_log()
    pre_amount = init_order() # get previous order amount
    sync_log() # replicate order log
    init_order()
    
    miss_orders(pre_amount)
    print(port, ' ', id)
    order_server.run(host=ip_addr, port=port, debug=True, threaded=True)

