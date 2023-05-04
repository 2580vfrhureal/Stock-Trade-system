import json
import os
from random import randint, random
from time import time
import requests

# get front_end server ip from env
FRONT_HOST = os.getenv('FRONT', 'localhost')
stocks_url = "http://%s:30001/stocks?stock_name=" % FRONT_HOST
order_url = "http://%s:30001/orders" % FRONT_HOST
p = os.getenv(
    'p', 0.5)  # Probability p can be set by command
p = float(p)
stocks = [
    'Stock1', 'Stock2', 'Stock3', 'Stock4', 'Stock5', 'Stock6', 'Stock7', 'Stock8',
    'Stock9', 'Stock10'
]
order_type = ['Buy','Sell']
success_order = [] # store successful order requests' info


# Mode 1: Query and Buy randomly
def client(s):
    start_time = time()
    r = requests.get(
        url=stocks_url + stocks[randint(0, 9)])  # Send an query request to front-end server
    end_time = time()
    print('query running time: ', end_time - start_time, 's')
    print(r.json())
    stock_name, quantity = r.json()['stock_name'], r.json()['quantity']
    if quantity > 0:  # If the returned quantity is greater than 0, with probability “p” it will send an order request
        if random() <= p:
            trade_type = order_type[randint(0,1)] # randomly select trade type
            num_trade = randint(1, 10)
            print('random trade: %s, trade type: %s, quantity: %s' % (stock_name,trade_type, num_trade))
            data = json.dumps({'stock_name': stock_name,'trade_type':trade_type, 'quantity': num_trade})
            start_time = time()
            resp = requests.post(
                url=order_url,  # Send an HTTP POST to front-end server
                data=data)
            end_time = time()
            if resp.status_code == 200:
                res = json.loads(resp.text)
                success_order.append({
                    "order_no": res["order_no"],
                    "stock_name": stock_name,
                    "trade_type": trade_type,
                    "quantity": num_trade,
                    })
            print('trade running time: ', end_time - start_time, 's')
            print(resp.json())
          


# 2 test stock query service
def query_stock(s):
    stock_name = input('input stock name(e.g:Stock1):\n')
    num = int(input('input request times:\n'))
    start_time = time()
    for i in range(num):
        r = requests.get(stocks_url + stock_name)  # Send a serials of HTTP GET to front-end server
        print(r.json())
    end_time = time()
    print('running time: ', end_time - start_time, 's')

# 3 query order
def query_order(s):
    order_query = input('input order_no:\n')
    num = int(input('input request times:\n'))
    start_time = time()
    for i in range(num):
        r = requests.get(order_url + '?order_no=' + str(order_query))  # Send a serials of HTTP GET to front-end server
        print(r.json())
    end_time = time()
    print('running time: ', end_time - start_time, 's')

# 4 trade service
def trade(s):
    stock_name = input('input the stock name you would like to trade: \n')
    trade_type = input('input trade type:Buy/Sell')
    quantity = int(input('input quantity:\n'))
    num = int(input('input request times:\n'))
    data = json.dumps({'stock_name': stock_name, 'trade_type':trade_type, 'quantity': quantity})
    start_time = time()
    for i in range(num):
        resp = requests.post(url=order_url,data=data) # Send an post request to front-end server
        print(resp.json())
    end_time = time()
    print('running time: ', end_time - start_time, 's')

# 5
def check_consistency():
    for order in success_order:
        order_query = order["order_no"]
        res = requests.get(order_url + '?order_no=' + str(order_query))
        r = json.loads(res.text)
        stock_name = r["data"]["stock_name"]
        trade_type = r["data"]["trade_type"]
        quantity =  r["data"]["quantity"]
        if stock_name == order["stock_name"] and trade_type == order["trade_type"] and int(quantity) == int(order["quantity"]):
            print("order info match with local!")
        else:
            print("not match with local")    

# Main
def main():
    s = requests.Session()
    while 1:
        msg = input('mode: \n')
        if str(msg) == '1':
            client(s)
        elif str(msg) == '2':
            query_stock(s)
        elif str(msg) == '3':
            query_order(s)
        elif str(msg) == '4':
            trade(s)
        elif str(msg) == '5':
            check_consistency()
            s.close()
        else:
            print('wrong code')


main()