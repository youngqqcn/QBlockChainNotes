#!coding:utf8

#author:yqq
#date:2019/9/17 0017 16:14
#description:
#     签名


import timeit

setup_str = '''
from eospy.cleos import EOSKey
import binascii
k = EOSKey("5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3")
digest=binascii.hexlify(b"a"*32)
'''
number=10
key_results=timeit.timeit('k=EOSKey("5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3")',
                          setup="from eospy.cleos import EOSKey", number=number)
print("Creating Key: Ran {} times and averaged {} seconds/run".format(number, key_results/number))

results=timeit.timeit('k.sign(digest)', setup=setup_str, number=number)

# print("Signing: Ran {} times and averaged {} seconds/run".format(number, results/number))