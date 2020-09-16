#!coding:utf8

#author:yqq
#date:2020/5/6 0006 16:48
#description:   测试 modle
# 关于  unittest 使用方法:  https://blog.51cto.com/2681882/2123613
# 1) 使用 TestSuite 可以控制测试用例的执行顺序
# 2) 如何让多个用例共用setup、teardown , 使用 setUpClass, tearDownClass
# 3) 如何跳过用例, unittest.skip(reason)、unittest.skipIf(condition,reason)、 unittest.skipUnless(condition,reason)
# 4) 如何生成html格式的测试报告:  使用HTMLTestRunner代替默认的TextTestRunner()



#参考: https://www.cnblogs.com/liu-yao/p/5342656.html
import redis as redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.handlers.accept_withdraw_order import AcceptWithdrawOrder
import unittest
import random
import json
import logging
import requests
# from src.monitor.eth_minitor_notify import scanner_trade
from src.api.handlers.handler_base import sign_msg
from src.config.constant import MYSQL_CONNECT_INFO

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s - %(message)s')

import time

# from test.test_user_api import mqsend
#
# serialid = "202005071948290024000"
# tx = {
#         "from":"htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2",
#         "to":"htdf1sg5av8alu6fqe06nuag9ctcgawrlzsj5szhcrx",
#         "value":1.00019999* (10**8)
#     }
# serial_id = { "serial_id" : serialid
# }

class TestAcceptWithdrawOrder(unittest.TestCase):
    # def addCleanup(self):
    #     这是清理函数
        # pass

    def setUp(self):
        """
        每个用例执行前调用此方法
        :return:
        """
        # mqsend(serial_id)
        pass

    def tearDown(self):
        print('tearDown()')

    @classmethod
    def tearDownClass(cls):
        """
        类
        :return:
        """
        print('tearDownClass()')
        pass

    # def shortDescription(self):
    #     pass


    @classmethod
    def setUpClass(cls):
        """
        在初始化类之前, 执行这个函数
        :return:
        "Hook method for setting up class fixture before running tests in the class."
        """
        cls.engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        SessionCls = sessionmaker(bind=cls.engine,
                                  autoflush=False,   #关于 autoflush https://www.jianshu.com/p/b219c3dd4d1e
                                  autocommit=True# 自动提交
                                  #  autocommit=False#自动提交
                                  )

        cls.session = SessionCls()

        print('setUpClass()')

    # def test_get_random_num(self):
    #     for i in range(19):
    #         num = random.uniform(0.001, 0.009)
    #         logging.info(num)

    def get_random_number_str(self, length):
        """
        生成随机数字字符串
        :param length: 字符串长度
        :return:
        """
        num_str = ''.join(str(random.choice(range(10))) for _ in range(length))
        return num_str

    def test_withdraw_order_post(self):


        REDIS_DEPOSIT_ADDRESS_POOL_NAME = 'deposit_address_sit'
        REDIS_HOST = '192.168.10.29'
        REDIS_PORT = 6379
        REDIS_DB_NAME = 1

        rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_NAME, decode_responses=True)


        req_count = 60 * 12
        n = 0
        # for i in range(req_count ):
        i = 0
        # token_list = ['HTDF', 'ETH', 'USDT']
        token_list = [ 'ETH', 'USDT']
        while True:

            # token = token_list[ i % 2]
            token = 'BTC'

            items = rds.srandmember(REDIS_DEPOSIT_ADDRESS_POOL_NAME, 1)
            to_address = ''
            if len(items) > 0:
                to_address  = items[0]

            if str(to_address).startswith('htdf1') and  token == 'HTDF':
                token_name = 'HTDF'
            elif str(to_address).startswith('0x'):
                if n % 5 == 0:
                    token = 'ETH'
                else:
                    token = 'USDT'
                token_name = token
                n += 1
            else:
                # print(f'invalid addresss:{to_address}')
                continue

            orderid = self.get_random_number_str(20)
            if(token_name) == "ETH":
                from_address = "0x13fd432b1e443f923065a3e48fc15a0ed270efcd"
                to_address = to_address
                amount = '0.10000001'#str(random.uniform(0.01, 0.009))[:8]
            elif(token_name == "USDT"):
                from_address = "0x13fd432b1e443f923065a3e48fc15a0ed270efcd"
                to_address = to_address
                amount = '0.100002' #str(random.uniform(0.1, 0.5))[:8]
            else: #(token_name == "HTDF"):
                from_address = "htdf1vhq6c38demm58cnevc4sntc77z8ppvl85mj0a6"
                to_address = to_address
                amount ='0.10000001' #str(random.uniform(0.1, 0.3))[:8]

            logging.info(f"from:{from_address}  ---> to:{to_address} amount:{amount}" )
            logging.info("orderid:%s, from_address:%s, to_address:%s==================== " % (orderid, from_address,to_address))
            data = {
                "order_id":orderid,
                "from_address":from_address,
                "to_address":to_address,
                "amount": amount ,
                "token_name":token_name,
                "pro_id":1,
                "callback_url":"http://192.168.10.29:8001/notify/withdraw"
            }


            jdata = json.dumps(data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

            # '1590040704197'
            timestamp = str(int(time.time() * 1000))
            # method  = 'POST'
            api_name = 'withdraw'

            param = '|'.join([timestamp, api_name, jdata])
            # print(param)

            msg = param.encode('utf8')
            sign_key = '9fb4d80781b34eac1b54f5631cc931133c42fd0decb2cda4738118996b416744'
            sig = sign_msg(sign_key=sign_key, msg=msg)
            sig = sig.decode('utf8')
            print(f'sig:{sig}')

            header = {
                # 'ContentType': 'application/json',
                'PG_API_KEY': '4575b80909ed0f2a09da77965f77b99a79b4182c66c7b51d002e134486bc1e97',
                'PG_API_TIMESTAMP': timestamp,
                'PG_API_SIGNATURE': sig
            }

            url = "http://192.168.10.174/api/withdraw/withdraw"
            # url = "http://192.168.10.29:8001/notify/withdraw"
            # url = "http://192.168.10.107:7778/api/withdraw/notifywithdraw"
            # url = "http://127.0.0.1:59002/withdraw"

            # import urllib3
            # import json

            # data = {'abc': '123'}
            # resp1 = urllib3.PoolManager(num_pools=5, headers=header)

            # resp1 = http.request('POST', url, fields=data)
            # resp1 = http.request('GET', 'http://www.httpbin.org/post', fields=data)

            # print(resp1.data.decode())


            rest = requests.post(url=url, json=data, headers=header)
            print(rest.text)

            # break
            #
            # ret_data = rest.json()
            # self.assertIsInstance(ret_data, dict)
            # self.assertIn('err_code', ret_data)
            # self.assertEqual(ret_data['err_code'], 0)
            #
            time.sleep(100)
            i += 1

    def test_withdraw_order_post_v2(self):


        # while True:
        if True:

            token_name = 'HTDF'
            to_address = 'htdf1rpuzcwy96y4rtksl6whmku0w8pwgjlykx2yu6e'

            orderid = self.get_random_number_str(20)
            data = {
                "order_id": orderid,
                "from_address": 'htdf1vhq6c38demm58cnevc4sntc77z8ppvl85mj0a6',
                "to_address": to_address,
                "amount": '0.1',
                "token_name": token_name,
                "pro_id": 1,
                "callback_url": "http://192.168.10.29:8001/notify/withdraw",
                "memo":"测"
            }

            jdata = json.dumps(data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序

            # '1590040704197'
            timestamp = str(int(time.time() * 1000))
            # method  = 'POST'
            api_name = 'withdraw'

            param = '|'.join([timestamp, api_name, jdata])
            # print(param)

            msg = param.encode('utf8')
            sign_key = 'bea7b5228628eaeffe3e595d389628ae9e2cdade0bfc093b606cf2e7b5db029c'
            sig = sign_msg(sign_key=sign_key, msg=msg)
            sig = sig.decode('utf8')
            print(f'sig:{sig}')

            header = {
                # 'ContentType': 'application/json',
                'PG_API_KEY': 'dafe466bad363682060c178a409ee9a7d35be178b2a51c98c3d12eb8c43e2a51',
                'PG_API_TIMESTAMP': timestamp,
                'PG_API_SIGNATURE': sig
            }

            # url = "http://192.168.10.174/api/withdraw/withdraw"
            url = "http://192.168.10.231/api/withdraw/withdraw"
            # url = "http://192.168.10.29:8001/notify/withdraw"
            # url = "http://192.168.10.107:7778/api/withdraw/notifywithdraw"
            # url = "http://127.0.0.1:59002/withdraw"


            rest = requests.post(url=url, json=data, headers=header)
            print(rest.text)





if __name__ == '__main__':
    test_funcs = [
        # TestAcceptWithdrawOrder('test_get_random_num')
        TestAcceptWithdrawOrder('test_withdraw_order_post')
        # TestAcceptWithdrawOrder('test_is_order_exists'),
        # TestModels('test_insert_data_WithdrawOrder'),
        # TestModels('test_query_data_WithdrawOrder'),
        # TestModels('test_insert_data_Project')
    ]

    suite = unittest.TestSuite()
    suite.addTests(test_funcs)

    runner = unittest.TextTestRunner()
    runner.run(test=suite)

    pass