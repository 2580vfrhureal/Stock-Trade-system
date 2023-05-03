from re import S
import unittest
import requests
import warnings
import json
import os

# Set IP adresseses of frontend, catalog and order as environment variables
FRONT = os.getenv('FRONT', 'localhost')
CATALOG = os.getenv('CATALOG', 'localhost')
ORDER = os.getenv('ORDER', 'localhost')
front_query_url = 'http://%s:30001/stocks?stock_name=' % FRONT
front_queryOrder_url = 'http://%s:30001/orders?order_no=' % FRONT
front_trade_url = 'http://%s:30001/orders' % FRONT
catalog_query_url = 'http://%s:10001/query?stock_name=' % CATALOG
catalog_trade_url = 'http://%s:10001/trade' % CATALOG
order_trade_url = 'http://%s:20003/trade?stock_name=' % ORDER
order_query_url = 'http://%s:20003/query?order_no=' % ORDER
order_ping_url = 'http://%s:20003/ping' % ORDER
order_leader_url = 'http://%s:20003/leader?leader=' % ORDER

class TestFunctions(unittest.TestCase):

    # front_end stock query service test
    def test_front_stocksQuery_valid(self): # 1
        r = requests.get(front_query_url + 'Stock1')
        actual = r.json()
        expected = {'stock_name': 'Stock1', 'price': 9.99, 'trade_volume': 0, 'quantity': 100}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_front_stocksQuery_invalid(self): # 2
        r = requests.get(front_query_url + 'invalid')
        actual = r.json()
        expected = {"error": {"code": 404, "message": "Stock not found"}}
        #warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
    
    # catalog query service test
    def test_catalog_query_valid(self): # 3
        r = requests.get(catalog_query_url + 'Stock1')
        actual = r.json()
        expected = {"data": {"stock_name": "Stock1", "price": 9.99, "trade_volume": 0,"quantity": 100}}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_catalog_query_invalid(self): # 4
        r = requests.get(catalog_query_url + 'invalid')
        actual = r.json()
        expected = {"error": {"code": 404, "message": "Stock not found"}}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    # order trade service test
    # test if url valid
    def test_order_buy_valid(self): # 5
        r = requests.get(order_trade_url + 'Stock1&trade_type=Buy&quantity=1')
        actual = r.json()
        expected = {"order_no": 1}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_order_sell_valid(self): # 6
        r = requests.get(order_trade_url + 'Stock1&trade_type=Sell&quantity=1')
        actual = r.json()
        expected = {"order_no": 2}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_order_trade_invalid(self): # 7
        r = requests.get(order_trade_url + 'invalid&trade_type=Buy&quantity=1')
        actual = r.json()
        expected = {"order_no": -1, "message": "Stock not found!"}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    #test if out of stock
    def test_order_trade_Buy_outofstock(self): # 8
        r = requests.get(order_trade_url + 'Stock1&trade_type=Buy&quantity=200')
        actual = r.json()
        expected = {"order_no": -1, "message": "Trade failed!"}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_order_trade_Sell_outofstock(self): # 9
        r = requests.get(order_trade_url + 'Stock1&trade_type=Sell&quantity=200')
        actual = r.json()
        expected = {"order_no": -1, "message": "Trade failed!"}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)


    # front end order service
    # test if url valid
    def test_front_buy_valid(self): # 10
        data = json.dumps({"stock_name": "Stock3","trade_type": "Buy","quantity": "1"})
        r = requests.post(url = front_trade_url, data = data)
        actual = r.json()
        expected  = {'order_no': 3}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_front_sell_valid(self): # 11
        data = json.dumps({"stock_name": "Stock3","trade_type": "Sell","quantity": "1"})
        r = requests.post(url = front_trade_url, data = data)
        actual = r.json()
        expected  = {'order_no': 4}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_front_trade_invalid(self): # 12
        data = json.dumps({"stock_name": "invalid","trade_type": "Buy","quantity": "1"})
        r = requests.post(url = front_trade_url, data = data)
        actual = r.json()
        expected = {'message': 'Stock not found!', 'order_no': -1}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    # test out of stock
    def test_front_buy_outofstock(self): # 13
        data = json.dumps({"stock_name": "Stock2","trade_type": "Buy", "quantity": "200"})
        r = requests.post(url = front_trade_url, data = data)
        actual = r.json()
        expected = {'message': 'Trade failed!', 'order_no': -1}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
        
    def test_front_sell_outofstock(self): # 14
        data = json.dumps({"stock_name": "Stock2","trade_type": "Sell", "quantity": "200"})
        r = requests.post(url = front_trade_url, data = data)
        actual = r.json()
        expected = {'message': 'Trade failed!', 'order_no': -1}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    # test catalog trade service
    def test_catalog_buy_valid(self): # 15
        data = json.dumps({"stock_name": "Stock3","type": "Buy", "quantity": "1"})
        r = requests.post(url = catalog_trade_url, data = data)
        actual = r.json()
        expected = {'message':'order had been trade successfully!'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_catalog_sell_valid(self): # 16
        data = json.dumps({"stock_name": "Stock3","type": "Sell", "quantity": "1"})
        r = requests.post(url = catalog_trade_url, data = data)
        actual = r.json()
        expected = {'message':'order had been trade successfully!'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)


    def test_catalog_trade_invalid(self): # 17
        data = json.dumps({"stock_name": "invalid","type": "Buy", "quantity": "1"})
        r = requests.post(url = catalog_trade_url, data = data)
        actual = r.json()
        expected = {'message':'Stock not found!'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
        
    def test_catalog_buy_outofstock(self): # 18
        data = json.dumps({"stock_name": "Stock3","type": "Buy", "quantity": "200"})
        r = requests.post(url = catalog_trade_url, data = data)
        actual = r.json()
        expected = {'message':'Trade failed!'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_catalog_sell_outofstock(self): # 19
        data = json.dumps({"stock_name": "Stock3","type": "Sell", "quantity": "200"})
        r = requests.post(url = catalog_trade_url, data = data)
        actual = r.json()
        expected = {'message':'Trade failed!'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
    
    # test front end order query service 
    def test_front_queryOrder_valid(self): # 20
        r = requests.get(front_queryOrder_url + '1')
        actual = r.json()
        expected = {'data': {'order_no': 1, 'stock_name': 'Stock1','trade_type':"Buy",'quantity': '1'}}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_front_queryOrder_invalid(self): # 21
        r = requests.get(front_queryOrder_url + '10')
        actual = r.json()
        expected = {'error': {'code': 404, 'message': 'order not found'}}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
    
    def test_order_queryOrder_valid(self): # 22
        r = requests.get(order_query_url + '2')
        actual = r.json()
        expected = {'data': {'order_no': 2, 'stock_name': 'Stock1','trade_type':"Sell",'quantity': '1'}}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)

    def test_order_queryOrder_invalid(self): # 23
        r = requests.get(order_query_url + '10')
        actual = r.json()
        expected = {'error': {'message': 'order not found', 'code': 404}}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
        
    def test_ping_valid(self): # 24
        r = requests.get(order_ping_url)
        actual = r.json()
        expected = {'alive order server': 3,'port':'20003'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
    
    def test_leader_valid(self): # 25
        r = requests.get(order_leader_url + '3')
        actual = r.json()
        expected = {'message': 'received leader id'}
        # warnings.simplefilter('ignore', ResourceWarning)
        self.assertEqual(actual, expected)
