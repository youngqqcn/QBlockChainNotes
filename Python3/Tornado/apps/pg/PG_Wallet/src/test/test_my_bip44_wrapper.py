#!coding:utf8

#author:yqq
#date:2020/5/8 0008 9:36
#description:



import unittest
from unittest import TestSuite, TextTestRunner, TestCase

from src.lib.my_bip44.wrapper import  gen_bip44_subaddr_from_mnemonic, \
    gen_bip44_subaddr_from_seed



class TestMyBIP44Wrapper(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.MNEMONIC = 'mother citizen apart father resemble coral section pony floor brother fuel lottery'
        pass

    def tearDown(self):
        pass



    def test_gen_bip44_subaddr_from_mnemonic(self):

        from src.lib.eth_wallet import Wallet
        wallet = Wallet()

        test_vector = [
            '0x2bdc01efe26c8a71d920472a6c7c6f2cfffe888a',  # 0
            '0x59ccc11420dea66bef173aaf5819abfcbf0b91ab',  # 1
            '0x3b8a2b1bcbdf4d9814902e1992d980d3ad27c07f',  # 2
            '0xaa6dd8015fadd860ee9a4c9ff036c490ed364f83',  # 3
            '0x881c5a50b294747a3b04dfa1e9708f67ff5ecbd4',  # 4
        ]
        wallet.from_mnemonic(mnemonic=self.MNEMONIC)

        for i in range(len(test_vector)):
            addr = gen_bip44_subaddr_from_mnemonic(self.MNEMONIC,
                                                   coin_type='ETH',
                                                   account_index=1,
                                                   address_index=i)

            # assert test_vector[i].lower() == addr.lower()
            self.assertEqual(test_vector[i].lower(), addr.lower())

        pass

    def test_gen_bip44_subaddr_from_seed(self):

        from src.lib.eth_wallet import Wallet
        wallet = Wallet()

        test_vector = [
            '0x2bdc01efe26c8a71d920472a6c7c6f2cfffe888a',  # 0
            '0x59ccc11420dea66bef173aaf5819abfcbf0b91ab',  # 1
            '0x3b8a2b1bcbdf4d9814902e1992d980d3ad27c07f',  # 2
            '0xaa6dd8015fadd860ee9a4c9ff036c490ed364f83',  # 3
            '0x881c5a50b294747a3b04dfa1e9708f67ff5ecbd4',  # 4
        ]
        wallet.from_mnemonic(mnemonic=self.MNEMONIC)
        seed = wallet.seed()

        for i in range(len(test_vector)):
            addr = gen_bip44_subaddr_from_seed(seed=seed ,
                                                   coin_type='ETH',
                                                   account_index=1,
                                                   address_index=i)

            self.assertEqual( test_vector[i].lower() , addr.lower()  )

        pass


    def test_gen_bip44_subaddr_from_mnemonic_HTDF(self):
        # test_addr = 'htdf1qgcfjpucqkcwk8n08mzur65tnqzuy3q6nge6ws'
        mnemonic = 'puzzle vanish isolate claw ugly ramp scheme sheriff asthma dream skin banana'
        tmp_addr = gen_bip44_subaddr_from_mnemonic( mnemonic=mnemonic,
                                        coin_type='ETH',
                                        account_index=1,
                                        address_index=100000000)
        print(tmp_addr)
        # self.assertEqual(test_addr, tmp_addr)

    def test_gen_bip44_subaddr_from_mnemonic_BTC(self):
        mnemonic = 'puzzle vanish isolate claw ugly ramp scheme sheriff asthma dream skin banana'
        tmp_addr = gen_bip44_subaddr_from_mnemonic( mnemonic=mnemonic,
                                        coin_type='BTC',
                                        account_index=1,
                                        address_index=100000000,
                                        nettype='mainnet'
                                        # nettype='testnet'
                                                    )
        print(tmp_addr)




def main():
    suite = unittest.TestSuite()

    suite.addTests([
        TestMyBIP44Wrapper('test_gen_bip44_subaddr_from_mnemonic'),
        TestMyBIP44Wrapper('test_gen_bip44_subaddr_from_seed'),
        TestMyBIP44Wrapper('test_gen_bip44_subaddr_from_mnemonic_HTDF'),
        TestMyBIP44Wrapper('test_gen_bip44_subaddr_from_mnemonic_BTC')
    ])

    runner = unittest.TextTestRunner()
    runner.run(test=suite)

    pass


if __name__ == '__main__':

    main()

