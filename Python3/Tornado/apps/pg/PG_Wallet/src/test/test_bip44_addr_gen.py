#!coding:utf8

#author:yqq
#date:2020/5/7 0007 18:00
#description:  测试 BIP44 规范私钥和子地址生成



import unittest
from unittest import TestSuite, TextTestRunner, TestCase


class TestBIP44AddrGen(TestCase):

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



    def test_eth_sub_account_addr_gen(self):
        """
        测试  子账户
        :return:
        """


        MNEMONIC = 'mother citizen apart father resemble coral section pony floor brother fuel lottery'


        from src.lib.eth_wallet import Wallet
        from src.lib.addr_gen.eth_addr_gen import gen_addr_from_privkey
        wallet = Wallet()

        test_vector = [
            '0x2bdc01efe26c8a71d920472a6c7c6f2cfffe888a',  # 0
            '0x59ccc11420dea66bef173aaf5819abfcbf0b91ab',  # 1
            '0x3b8a2b1bcbdf4d9814902e1992d980d3ad27c07f',  # 2
            '0xaa6dd8015fadd860ee9a4c9ff036c490ed364f83',  # 3
            '0x881c5a50b294747a3b04dfa1e9708f67ff5ecbd4',  # 4
        ]

        for i in range(len(test_vector)):
            wallet.from_mnemonic(mnemonic=MNEMONIC)
            addr_path = f"m/44'/60'/1'/0/{i}"
            wallet.from_path(addr_path)
            # print( wallet.public_key() )
            # print(wallet.private_key())
            # print( json.dumps( wallet.dumps() , indent=4) )
            priv_key = wallet.private_key()
            addr = gen_addr_from_privkey( priv_key=priv_key )
            print(addr)
            assert test_vector[i].lower() == addr.lower()

        pass

    def test_eth_sub_addr_gen(self):
        from src.lib.eth_wallet import Wallet
        from src.lib.addr_gen.eth_addr_gen import gen_addr_from_privkey
        MNEMONIC = 'mother citizen apart father resemble coral section pony floor brother fuel lottery'
        wallet = Wallet()

        test_vector = [
            '0x954d1a58c7abd4ac8ebe05f59191Cf718eb0cB89',  # 0
            '0xc6a6FdBcab9eA255eDEE2e658E330a62f793B74E',  # 1
            '0xdf88522B56B85d4F0Bb08a7494b97E017BC6CB31',  # 2
            '0x99F239694CbF9753B8ad649E34AcF4359cb5caF0',  # 3
            '0xD2F8f3fBc27745b9fa4f5299c1812f4b95aC9F91',  # 4
        ]

        for i in range(len(test_vector)):
            wallet.from_mnemonic(mnemonic=MNEMONIC)
            addr_path = f"m/44'/60'/0'/0/{i}"
            wallet.from_path(addr_path)
            # print( wallet.public_key() )
            # print(wallet.private_key())
            # print( json.dumps( wallet.dumps() , indent=4) )
            addr = gen_addr_from_privkey(wallet.private_key())
            assert test_vector[i].lower() == addr.lower()

        pass

    def test_htdf_sub_account_addr_gen(self):
        """
        测试  子账户
        :return:
        """


        MNEMONIC = 'mother citizen apart father resemble coral section pony floor brother fuel lottery'


        from src.lib.eth_wallet import Wallet
        from src.lib.addr_gen.eth_addr_gen import gen_addr_from_privkey
        wallet = Wallet()

        test_vector = [
            # '0x2bdc01efe26c8a71d920472a6c7c6f2cfffe888a',  # 0
            # '0x59ccc11420dea66bef173aaf5819abfcbf0b91ab',  # 1
            # '0x3b8a2b1bcbdf4d9814902e1992d980d3ad27c07f',  # 2
            # '0xaa6dd8015fadd860ee9a4c9ff036c490ed364f83',  # 3
            # '0x881c5a50b294747a3b04dfa1e9708f67ff5ecbd4',  # 4
        ]

        for i in range(len(test_vector)):
            wallet.from_mnemonic(mnemonic=MNEMONIC)
            addr_path = f"m/44'/346'/9'/0/{i}"
            wallet.from_path(addr_path)
            # print( wallet.public_key() )
            # print(wallet.private_key())
            # print( json.dumps( wallet.dumps() , indent=4) )
            priv_key = wallet.private_key()
            addr = gen_addr_from_privkey( priv_key=priv_key )
            print(addr)
            # assert test_vector[i].lower() == addr.lower()

        pass


#
# def main():
#     suite = unittest.TestSuite()
#
#     suite.addTests([
#         # TestBIP44AddrGen('test_eth_sub_account_addr_gen'),
#         # TestBIP44AddrGen('test_eth_sub_addr_gen'),
#         TestBIP44AddrGen('test_htdf_sub_account_addr_gen')
#     ])
#
#     runner = unittest.TextTestRunner()
#     runner.run(test=suite)
#
#     pass
#
#
# if __name__ == '__main__':
#
#     main()