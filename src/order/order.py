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
@order_server.route('/query', methods=['GET'])
def query():
    order_no = request.args.get('order_no')
    for item in order_db:
        if item['order_no'] == int(order_no):
            res = json.dumps({
                'data': {
                    'order_no': order_db['order_no'],
                    'stock_name': order_db['stock_name'],
                    'trade_type': order_db['trade_type'],
                    'quantity': order_db['quantity']
                }
            })
            return res
    res = json.dumps({'error': {'code': 404, 'message': 'order not found'}})
    return res, 404


# process order
@order_server.route('/orders', methods=['GET'])
def orders():
    stock_name = request.args.get('stock_name')
    trade_type = request.args.get('trade_type')
    quantity = request.args.get('quantity')
    data = json.dumps({'stock_name': stock_name, 'trade_type':trade_type, 'quantity': quantity})
    r = requests.post('http://0.0.0.0:10001/trade', data=data)
    if r.status_code == 200:
        order_no = order_log.increment()
        res = json.dumps({"order_no": order_no})
        with lock:
            order_db.append({
                'order_no': order_no,
                'stock_name': stock_name,
                'trade_type': trade_type,
                'quantity': quantity
            })
            f = open('order_log%s.txt' % id, 'a+')
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
        with lock:
            order_db.append({
                'order_no': order_no,
                'stock_name': stock_name,
                'trade_type': trade_type,
                'quantity': quantity
            })
            f = open('order_log%s.txt' % id, 'a+')
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
        return res, 404
    else:
        return 'Unknown Error%s' % r.status_code


# sync order log with the leader node
@order_server.route('/sync', methods=['POST'])
def notify():
    data = request.get_json()
    data = json.loads(data)
    print(data)
    order_no, stock_name, trade_type,quantity = data['order_no'], data['stock_name'], data['trade_type'],data['quantity']
    # if the order is success, increase id stored in memory by one
    # in order to consistent order num with leader
    if order_no!=-1:
        order_log.increment()
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
                requests.post('http://0.0.0.0:%s/sync' % order,data=data)
            except Exception:
                print('%s sync failed!' % order)
        i += 1

# when leader is selected
@order_server.route('/leader', methods=['GET'])
def leader():
    global leader_id
    leader_id = request.args.get('leader')
    return json.dumps({'message': 'received leader id'})


# alive API
@order_server.route('/alive', methods=['GET'])
def heartbeat():
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
                    'number': info[0],
                    'name': info[1],
                    'quantity': info[2]
                }
                order_db.append(item)
        f.close()

# replica order_log from other nodes
def replica_log():
    if os.path.exists('order_log1.txt') or os.path.exists(
            'order_log2.txt') or os.path.exists('order_log3.txt'):
        if id == 1:
            copyfile('order_log2.txt', 'order_log1.txt')
        else:
            source_file = 'order_log%s.txt' % ((id - 1) % 3)
            dis_file = 'order_log%s.txt' % id
            copyfile(source_file, dis_file)


if __name__ == '__main__':
    id = int(os.getenv('ID', 5))
    port = os.getenv('PORT', 10010)
    replica_log()
    id_gen = order_log()
    init_order()
    print(order_db)
    print(port, ' ', id)
    order_server.run(host='0.0.0.0', port=port, threaded=True)
