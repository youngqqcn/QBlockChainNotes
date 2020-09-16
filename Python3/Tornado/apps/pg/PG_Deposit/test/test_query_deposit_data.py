#!coding:utf8

#author:yqq
#date:2020/5/21 0021 16:57
#description: 测试用例
import json
import time
import unittest

import requests

from src.api.handlers.handler_base import sign_msg


class TestQueryDepositOrder(unittest.TestCase):

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

    def test_query_deposit_data(self):

        data = {
            'pro_id': 1,
            # 'token_name': 'HTDF',
            'token_name': 'BTC',
            'start_height': 0,
            'end_height': 999999999,
            'page_index': 1,
            'page_size': 2,
        }

        jdata = json.dumps(data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

        # '1590040704197'
        timestamp = str(int(time.time() * 1000))
        # method  = 'POST'
        api_name = 'getdepositdata'

        param = '|'.join([timestamp, api_name, jdata])
        # print(param)

        msg = param.encode('utf8')
        sign_key = '9fb4d80781b34eac1b54f5631cc931133c42fd0decb2cda4738118996b416744'
        sig = sign_msg(sign_key=sign_key, msg=msg)
        sig = sig.decode('utf8')
        print(f'sig:{sig}')

        header = {
            'ContentType': 'application/json',
            'PG_API_KEY': '4575b80909ed0f2a09da77965f77b99a79b4182c66c7b51d002e134486bc1e97',
            'PG_API_TIMESTAMP': timestamp,
            'PG_API_SIGNATURE': sig
        }

        url = "http://192.168.10.174/api/deposit/getdepositdata"
        # url = "http://127.0.0.1:59000/getdepositdata"
        rest = requests.post(url=url, json=data, headers=header)


        print( json.dumps(json.loads(rest.text), indent=4))

        pass



def main():
    suite = unittest.TestSuite()

    suite.addTests([
        TestQueryDepositOrder('test_query_deposit_data'),
    ])

    runner = unittest.TextTestRunner()
    runner.run(test=suite)


    pass


if __name__ == '__main__':

    main()