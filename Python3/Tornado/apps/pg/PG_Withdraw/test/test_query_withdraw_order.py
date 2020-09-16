#!coding:utf8

#author:yqq
#date:2020/5/21 0021 16:57
#description: 测试用例
import json
import time
import unittest

import requests

from src.api.handlers.handler_base import sign_msg


class TestQueryWithdrawOrder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_query_withdraw_order(self):

        data = {
            'pro_id':1,
            'serial_id' : '202005211652543548069'
        }

        jdata = json.dumps(data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

        # '1590040704197'
        timestamp = str(int(time.time() * 1000))
        # method  = 'POST'
        api_name = 'querywithdraworder'

        param = '|'.join([timestamp, api_name, jdata])
        # print(param)

        msg = param.encode('utf8')
        sign_key = '3e4b948ae2a54554d13138d64c5fb6b9764489099803f2f7360306d8e9db98f8'
        sig = sign_msg(sign_key=sign_key, msg=msg)
        sig = sig.decode('utf8')
        print(f'sig:{sig}')

        header = {
            'ContentType': 'application/json',
            'PG_API_KEY': 'd5a08d84603f5714914bf39915d198b501e8f389e31fe12ec6f18d7b906f5c0c',
            'PG_API_TIMESTAMP': timestamp,
            'PG_API_SIGNATURE': sig
        }

        # url = "http://192.168.10.174/api/withdraw/withdraw"
        url = "http://127.0.0.1:59001/querywithdraworder"
        rest = requests.post(url=url, json=data, headers=header)
        print(rest.text)

        pass

    def test_query_all_withdraw_order(self):
        pro_id = 1
        post_data = {
            # 'address_count': address_count,
            # 'account_index': account_index,
            'pro_id': pro_id,
            'token_name': 'HTDF',
            'start_time': 0,
            'end_time': 9999999999,
            'page_index': 1,
            'page_size': 20
        }

        jdata = json.dumps(post_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

        # '1590040704197'
        timestamp = str(int(time.time() * 1000))
        # method  = 'POST'
        api_name = 'queryallwithdrawdata'

        param = '|'.join([timestamp, api_name, jdata])
        # print(param)

        msg = param.encode('utf8')
        sign_key = '3e4b948ae2a54554d13138d64c5fb6b9764489099803f2f7360306d8e9db98f8'
        sig = sign_msg(sign_key=sign_key, msg=msg)
        sig = sig.decode('utf8')
        print(f'sig:{sig}')

        header = {
            'ContentType': 'application/json',
            'PG_API_KEY': 'd5a08d84603f5714914bf39915d198b501e8f389e31fe12ec6f18d7b906f5c0c',
            'PG_API_TIMESTAMP': timestamp,
            'PG_API_SIGNATURE': sig
        }

        url = "http://192.168.10.174/api/withdraw/queryallwithdrawdata"
        # url = "http://127.0.0.1:59001/querywithdraworder"
        rest = requests.post(url=url, json=post_data, headers=header)
        print(rest.text)

        pass



def main():
    suite = unittest.TestSuite()

    suite.addTests([
        TestQueryWithdrawOrder('test_query_withdraw_order'),
    ])

    runner = unittest.TextTestRunner()
    runner.run(test=suite)


    pass


if __name__ == '__main__':

    main()