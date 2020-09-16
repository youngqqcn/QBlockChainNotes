#!coding:utf8

# author:yqq
# date:2020/5/7 0007 17:23
# description: 测试地址生成的  测试用例


import unittest
from unittest import TestSuite, TextTestRunner, TestCase


class TestAddressGenerateFunctions(TestCase):

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

    def test_htdf_addr_gen_func(self):
        """
        测试 HTDF 地址生成
        :return:
        """

        from src.lib.addr_gen.htdf_addr_gen import gen_addr_from_privkey

        test_htdf_vector = [('03ca0713fcd2a17d78ef014e59767647445db876b0b4827782c1d02ee539f25d',
                             'htdf1njlhnautfwtwae8n5y685xre7ah4qjnnel3d5e'), (
                                'd229d315054006ba8b0732344d486a0184e0b35f6ac58effda899c2cca80a50f',
                                'htdf1a6zpe26qhq65d5l6qalrfj3taprg53yuryk3x9'), (
                                '9e348457fa47ca63ba237440e76ae310c0d5bf8348f74053fb0268f293461465',
                                'htdf1syuyhr4shylqy8upfe8dt54w6dp85d2sksn9sc'), (
                                '1211c43de956f783bb5c9cc2f148a6737d79e2350b74a25e76a1bb9a521c9eb5',
                                'htdf1xw5v66qq2mh3zl5czjhz6e586atslxky5vl3ts'), (
                                '7963bd3fa0c1743a2398d9e8663400bd7bee280b5bba21ecce16be591eca12ba',
                                'htdf1a3l6ppk2s9jvn0xaxgcxhpqfjr2ku52476t0j8'), (
                                '283dd7de951ba5b798f7e6b8074380c6780a5b3838de9de404f34dbe3eaad72e',
                                'htdf1fhyzd5dpezqqlp4yqurjr0yaatnw9774jhmd43'), (
                                '3b25a064a5fdecb014e45c18463b5dde4b144997da732dae5a7cfce8157f96ef',
                                'htdf1n7xd82dretajcdruv84zd2cnzz3ghguz7ed3mr'), (
                                'ca784a704a08bf3d839ce49db7279a392311b9fd7a08ec8462e8c2809a18ee0c',
                                'htdf12gj7cra7ln4ck03z8sksu0vwj5jhzsgmuthlhg'), (
                                '55e12c953051d85ae4510a6b363bb47056697fd95e6a745477ed85b82c864a91',
                                'htdf1cg29dg50wytyv6uhakrz0j4kx4cgjy8p0qhfk2'), (
                                'cdb5d5776c340ab2296a098cf381f46f964227edf75844c8530797253832a80a',
                                'htdf1xugpnwlep6y3uq7m35e855s48hzk4kx309shg8')]

        for tup in test_htdf_vector:
            priv_key = tup[0]

            result = tup[1].lower().strip()

            addr_tmp = gen_addr_from_privkey(priv_key=priv_key).lower().strip()

            self.assertEqual(first=result, second=addr_tmp, msg=f'{result} != {addr_tmp}')

        pass

    def test_eth_addr_gen_func(self):
        """
        测试 ETH 地址生成
        :return:
        """

        from src.lib.addr_gen.eth_addr_gen import gen_addr_from_privkey


        eth_test_vector = [('d3e011c6ab37a51ced283778031e151281e8994881f7998e6523868171b78510',
                            '0xf9faf24792602ff41a2040dfb9ea5e0a7dee2865'), (
                           'fcbb316b11cb3f3c009dcc43c8e955928fd4d6007c71e745d210039187101097',
                           '0x0c29ceee50e67cc8a1bb432403d9d64de555b3ee'), (
                           'bcef6f9fb11cda92bd79d189fe2cec09c30d97d46eb65592d82d93582fb49432',
                           '0xac612a3fa123c7195e90140448b51667cc56cac1'), (
                           '3c11a1a585451e549bfc1e69055a365bc8c144b6bb4ac2a4fb821b331ca25769',
                           '0x9514861efc238e31bc96bb9ac3c2194decc905d0'), (
                           '133488b93664d01d97ce1c44cb3a0cfd354fa9863bd9524e8dcb01925b3d3b22',
                           '0xbf6cff8e1f0f4926ad5c46236252b1b4f5e26def'), (
                           '214222c024328db78e3a53949925441c9e0360acd222f8534791c7c551a75e36',
                           '0x790996ea9b79792cb50c15c67f467d804c409e99'), (
                           'b3e7ae3770c8d902b23d978fb126403e44fc123a0cdc40b655b71031068091d2',
                           '0x324faa63fd8dcf1d32c1c98dad97b3ab5e8068bb'), (
                           '94b1291c14946d5d2f16e1b9a3ec04974b6b6a2e2e1d01f21615f0c3c1595de6',
                           '0x0b35a5f189f538a190a7fc185d8242be1872686a'), (
                           '25538e504bd51fd7d32e1bf43cce03e94957dff74fe8bfb966521f000ecd0b90',
                           '0x762bd90eb33b2a4110f624f03f280c8c05a24114'), (
                           'd57dcd35831a7e6f81f559c463a83f43e446b8e25bf2b00cbcb75f1c1d147641',
                           '0x05bb3d5e9780966902d4743d1378a786802fec11')]

        for tup in eth_test_vector:
            priv_key = tup[0]

            result = tup[1].lower().strip()

            addr_tmp = gen_addr_from_privkey(priv_key=priv_key).lower().strip()

            self.assertEqual(first=result, second=addr_tmp, msg=f'{result} != {addr_tmp}')

        pass

    pass


if __name__ == '__main__':
    # unittest.main()

    suite = unittest.TestSuite()

    suite.addTests([
        TestAddressGenerateFunctions('test_eth_addr_gen_func'),
        TestAddressGenerateFunctions('test_htdf_addr_gen_func')
    ])

    runner = unittest.TextTestRunner()
    runner.run(test=suite)

    pass
