#!coding:utf8

#author:yqq
#date:2019/12/30 0030 11:23
#description:


import eospy
import eospy.cleos
import eospy.keys
from eospy.cleos import Cleos


class EosProxy(Cleos):

    def  __init__(self, url):
        Cleos.__init__(self=self, url=url)
        pass

    def sendrawtransaction(self, data , timeout=30):
        return self.post('chain.push_transaction', params=None, data=data, timeout=timeout)

