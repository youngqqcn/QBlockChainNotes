#!coding:utf8

#author:yqq
#date:2019/12/6 0006 10:33
#description:  获取充币数据


# from  ripple_api import RippleDataAPIClient
from  lib.ripple_proxy.ripple_proxy import RippleProxy
from pprint import pprint
import time

import unittest

class TestRippleLib( unittest.TestCase ):

    def setUp(self):
        self.ripple_api = RippleProxy('http://data.ripple.com')
        pass

    def tearDown(self):
        pass

    def test_ledgers(self):
        print('test /v2/ledgers/')
        identifier = '3170DA37CE2B7F045F889594CBC323D88686D2E90E8FFD2BBCD9BAD12E416DB5'
        # query_params = dict(transactions=True, expand=True)
        query_params = dict(transactions=True)
        ledger_info = self.ripple_api.get_ledger(ledger_identifier=identifier, **query_params)
        pprint(ledger_info)
        self.assertIsNotNone(ledger_info, "ledger_info is none")

    def test_get_account_balances(self):
        balances = self.ripple_api.get_account_balances(address='r3Vh1bZbktiWRyJBe6BB9H3okW577u37BE')
        pprint(balances)
        self.assertIsNotNone(balances, " balances  is none")

    def test_get_account_transactions_history(self):
        address = "r3Vh1bZbktiWRyJBe6BB9H3okW577u37BE"
        # time_array = time.strptime('2019-08-06T14:28:40+00:00', "%Y-%m-%dT%H:%M:%S%z")
        time_array = time.strptime("2019-08-01T14:55:11+00:00", "%Y-%m-%dT%H:%M:%S%z")
        nstart_time = int( time.mktime(time_array) )
        tx_type = 'Payment'
        result = 'tesSUCCESS'
        limit = 999
        options = dict( type=tx_type, result=result, limit=limit , start=nstart_time)
        txs =  self.ripple_api.get_account_transaction_history(address=address, **options)
        pprint(txs)
        self.assertIsNotNone(txs, 'txs is none')



def main():
    # api = RippleDataAPIClient('https://data.ripple.com')
    # api = RippleDataAPIClient('http://data.ripple.com')
    # identifier = '3170DA37CE2B7F045F889594CBC323D88686D2E90E8FFD2BBCD9BAD12E416DB5'
    # query_params = dict(transactions='true')
    # ledger_info = api.get_ledger(ledger_identifier=identifier, **query_params)
    # pprint(ledger_info)


    #test pass
    # balances = api.get_account_balances(address='r3Vh1bZbktiWRyJBe6BB9H3okW577u37BE')
    # pprint(balances)


    # unittest.main()

    suite = unittest.TestSuite()
    # tests = [ TestRippleLib("test_ledgers") ]
    # tests = [ TestRippleLib("test_get_account_transactions_history") ]
    # suite.addTests(tests)

    suite.addTest( TestRippleLib("test_get_account_transactions_history") )

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


    pass


if __name__ == '__main__':

    main()