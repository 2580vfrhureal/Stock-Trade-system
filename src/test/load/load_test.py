import json
import socket
from time import sleep
import unittest
import requests
import warnings
import os

FRONT = os.getenv('FRONT', 'localhost')
queryStock_url = 'http://%s:30001/stocks?stock_name=' % FRONT
queryOrder_url = 'http://%s:30001/orders?order_no=' % FRONT
trade_url = 'http://%s:30001/orders' % FRONT

class TestLoadPerformance(unittest.TestCase):

    def test_load_query(self):
        #warnings.simplefilter('ignore', ResourceWarning)
        for i in range(1000):
            res = requests.get(queryStock_url + 'Stock1')

    def test_load_queryOrder(self):
        #warnings.simplefilter('ignore', ResourceWarning)
        for i in range(1000):
            res = requests.get(queryOrder_url + '30')

    def test_load_trade(self):
        #warnings.simplefilter('ignore',ResourceWarning)
        data = json.dumps({"stock_name": "Stock1","trade_type": "Buy", "quantity": "1"})
        for i in range(100):
            res = requests.post(url = trade_url, data = data)
            
    
