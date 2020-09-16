#!coding:utf8

#author:yqq
#date:2020/5/8 0008 15:15
#description: 测试用例
import json
import string
import time
import unittest
import requests
from ed25519 import SigningKey

from src.api.handlers.handler_base import sign_msg, verify_sig


class TestWalletAPI(unittest.TestCase):

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
    


    def test_getcollectiondata(self):

        pro_id = 1
        # url = 'http://127.0.0.1:59009/queryaddresses'
        url = 'http://192.168.10.174/api/collection/getcollectiondata'

        # for token_name in ['HTDF', 'ETH']:
        post_data = {
            # 'address_count': address_count,
            # 'account_index': account_index,
            'pro_id': pro_id,
            'token_name': 'BTC',
            'start_time' : 0,
            'end_time' : 9999999999,
            'page_index':1,
            'page_size':20
        }

        # header = {
        #     'ContentType': 'application/json'
        # }

        jdata = json.dumps(post_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

        # '1590040704197'
        timestamp = str(int(time.time() * 1000))
        # method  = 'POST'
        api_name = 'getcollectiondata'

        param = '|'.join([timestamp, api_name, jdata])
        # print(param)

        msg = param.encode('utf8')
        sign_key = '9fb4d80781b34eac1b54f5631cc931133c42fd0decb2cda4738118996b416744'
        # sk = SigningKey(sk_s=sign_key.encode('latin1'), prefix='', encoding='hex')
        # sig = sk.sign(msg=msg, prefix='', encoding='base64')
        sig = sign_msg(sign_key=sign_key, msg=msg)
        sig = sig.decode('utf8')
        print(f'sig:{sig}')
        # if verify_sig(verify_key=ASCCI_VERIFY_KEY, sig=sig, msg=msg):
        #     print('verify ok')
        # else:
        #     print('verify failed')
        header = {
            'ContentType': 'application/json',
            'PG_API_KEY': '4575b80909ed0f2a09da77965f77b99a79b4182c66c7b51d002e134486bc1e97',
            'PG_API_TIMESTAMP': timestamp,
            'PG_API_SIGNATURE': sig
        }



        rsp = requests.post(url=url, json=post_data, headers=header)

        self.assertEqual(rsp.status_code, 200)

        rsp_data = rsp.json()
        print(rsp_data)

        pass
    
    

def main():
    suite = unittest.TestSuite()

    suite.addTests([
        TestWalletAPI('test_generateaddress'),
    ])

    runner = unittest.TextTestRunner()
    runner.run(test=suite)


    pass


if __name__ == '__main__':

    main()