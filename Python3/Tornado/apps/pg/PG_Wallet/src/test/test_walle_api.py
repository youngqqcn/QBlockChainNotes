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
    
    def test_generateaddress(self):

        # url = 'http://127.0.0.1:59009/addaddresses'


        address_count = 10
        pro_id = 52

        # for token_name in ['BTC', 'HTDF', 'ETH']:
        for token_name in ['ETH']:
            post_data = {
                'address_count': address_count,
                # 'account_index': account_index,
                'pro_id': pro_id,
                'token_name': token_name,
            }



            jdata = json.dumps(post_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

            # '1590040704197'
            timestamp =  str(int(time.time() * 1000))
            # method  = 'POST'
            api_name = 'addaddresses'

            param = '|'.join([timestamp, api_name, jdata])
            # print(param)

            msg = param.encode('utf8')
            sign_key = '2ed28bf53120a4d07ce82e614be060a15322563bada59f16d2ac1f7c323acdb0'
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
                'PG_API_KEY':'1f0e774c81e2b3545493a76873d019b42d2273a617535b3848dcca17e7334efe',
                'PG_API_TIMESTAMP':timestamp,
                'PG_API_SIGNATURE':sig
            }



            rsp = requests.post(url='http://192.168.10.174/api/wallet/addaddresses', json=post_data, headers=header)
            # rsp = requests.post(url='http://192.168.10.155:59000/addaddresses', json=post_data, headers=header)

            self.assertEqual(rsp.status_code, 200)

            rsp_data = rsp.json()
            print(rsp_data)


        pass

    def test_queryaddress(self):

        pro_id = 1
        url = 'http://127.0.0.1:59000/queryaddresses'
        # url = 'http://192.168.10.174/api/wallet/queryaddresses'

        for token_name in ['HTDF', 'ETH']:
            post_data = {
                'pro_id': pro_id,
                'token_name': token_name,
                'page_index':1,
                'page_size':1,
                'order_id':'202006081010508973077'
            }

            jdata = json.dumps(post_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

            timestamp = str(int(time.time() * 1000))
            api_name = 'queryaddresses'

            param = '|'.join([timestamp, api_name, jdata])

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

            rsp = requests.post(url=url, json=post_data, headers=header)

            self.assertEqual(rsp.status_code, 200)

            rsp_data = rsp.json()
            print(rsp_data)

            break
        pass

    def test_queryaddaddressorder(self):

        # pro_id = 1
        # url = 'http://127.0.0.1:59009/queryaddaddressesorder'
        url = 'http://192.168.10.174/api/wallet/queryaddaddressesorder'

        if True:
            post_data = {
                'pro_id': 1,
                'order_id':'202005281828093277212'
            }

            jdata = json.dumps(post_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

            timestamp = str(int(time.time() * 1000))
            api_name = 'queryaddaddressesorder'

            param = '|'.join([timestamp, api_name, jdata])

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

            rsp = requests.post(url=url, json=post_data, headers=header)

            self.assertEqual(rsp.status_code, 200)

            rsp_data = rsp.json()
            print(rsp_data)


    

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