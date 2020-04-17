#!coding:utf8

#author:yqq
#date:2019/8/28 0028 14:22
#description:  ETH 普通转账  /  ERC20 代币转账

from ethereum.transactions import  Transaction
import rlp
from rlp.sedes import big_endian_int , binary
from decimal import  Decimal

from binascii import unhexlify, hexlify



#普通的ETH转账成功的案例: https://rinkeby.etherscan.io/address/0x56e5782c908f69bd46b7e77338349f961fbe55b1
#ERC20-Token的转账成功案例: https://rinkeby.etherscan.io/tx/0xfa8da3dda31d644a5f654fc332284cafc2367990a529a14fdb0085b2e89259aa
#ERC20-Token 假交易的案例: https://rinkeby.etherscan.io/tx/0xa5c51ead7f209ac97fb8d8685171e2a5fc50bfb98b987cb6e3342670e9919b3a
#

Mainnet=0
Rinkeby=4


def to_zero_padded_str(in_data, target_len=64):
    # print(in_data)
    return '0' * (target_len - len(in_data)) + in_data


def make_data(abi_transfer='a9059cbb', to='0x123423', value=0x123424):
    return abi_transfer + to_zero_padded_str(to[2:]) + to_zero_padded_str(hex(int(value))[2:].replace('L', ''))
    pass


def main():

    erc20_data =  make_data(to='0x56e5782c908f69bd46b7e77338349f961fbe55b1', value=Decimal('2019.08281809')*(10**18))
    print( "erc20_data:{}".format( erc20_data) )

    tx = Transaction(nonce=120,
                     gasprice=10*(10**9),
                     startgas=210000,
                     to='0x130fc2749d35fe026f32427f60dd3f2ecb6c2f33',
                     value=0,
                     # data=b''
                     data = erc20_data.decode('hex')
                     )
    tx.sender = '0x954d1a58c7abd4ac8ebe05f59191cf718eb0cb89'

    # print(tx.hash)
    signed_tx  =  tx.sign(key='DBBAD2A5682517E4FF095F948F721563231282CA4179AE0DFEA1C76143BA9607', network_id=Rinkeby)  # 4:Rinkeby
    print( signed_tx.hash.encode('hex'))
    rlp_data = rlp.encode(  rlp.infer_sedes(tx).serialize(tx) )
    print(rlp_data.encode('hex'))
    # print(signed_tx)

    pass


def main2():

    erc20_data =  make_data(to='0xdf88522B56B85d4F0Bb08a7494b97E017BC6CB31', value=Decimal('656340.20627410')*(10**18))
    print( "erc20_data:{}".format( erc20_data) )

    tx = Transaction(nonce=51,
                     gasprice=10*(10**9),
                     startgas=210000,
                     to='0x130fc2749d35fe026f32427f60dd3f2ecb6c2f33',
                     value=1*(10**16),
                     # data=b''
                     data = erc20_data.decode('hex')
                     )
    tx.sender = '0x56e5782c908f69bd46b7e77338349f961fbe55b1'

    # print(tx.hash)
    signed_tx  =  tx.sign(key='63C08FABC252B53B9471E520CE8199971DB8884B5B569CBBBD17BC714E6BB39F', network_id=Rinkeby)  # 4:Rinkeby
    print( signed_tx.hash.encode('hex'))
    rlp_data = rlp.encode(  rlp.infer_sedes(tx).serialize(tx) )
    print(rlp_data.encode('hex'))
    # print(signed_tx)

    pass




#  BJC
def main3():

    erc20_data =  make_data(to='0x401bf316182c792048c75e52ce18cb12ec3c4273', value=Decimal('65.20627410')*(10**18))
    print( "erc20_data:{}".format( erc20_data) )

    tx = Transaction(nonce=58,
                     gasprice=10*(10**9),
                     startgas=210000,
                     to='0xee8e2882e07f89685430c27e2f77636b08df3c81',
                     value=1,
                     # data=b''
                     data = erc20_data.decode('hex')
                     )
    tx.sender = '0x56e5782c908f69bd46b7e77338349f961fbe55b1'

    # print(tx.hash)
    signed_tx  =  tx.sign(key='63C08FABC252B53B9471E520CE8199971DB8884B5B569CBBBD17BC714E6BB39F', network_id=Rinkeby)  # 4:Rinkeby
    print( signed_tx.hash.encode('hex'))
    rlp_data = rlp.encode(  rlp.infer_sedes(tx).serialize(tx) )
    print(rlp_data.encode('hex'))
    # print(signed_tx)

    pass


#  BJC
def main3_py3():

    erc20_data =  make_data(to='0x401bf316182c792048c75e52ce18cb12ec3c4273', value=Decimal('65.20627410')*(10**18))
    print( "erc20_data:{}".format( erc20_data) )

    tx = Transaction(nonce=58,
                     gasprice=10*(10**9),
                     startgas=210000,
                     to='0xee8e2882e07f89685430c27e2f77636b08df3c81',
                     value=1,
                     # data=b''
                     data = unhexlify( erc20_data)
                     )
    tx.sender = '0x56e5782c908f69bd46b7e77338349f961fbe55b1'

    # print(tx.hash)
    signed_tx  =  tx.sign(key='63C08FABC252B53B9471E520CE8199971DB8884B5B569CBBBD17BC714E6BB39F', network_id=Rinkeby)  # 4:Rinkeby
    # print( hexlify(signed_tx.hash) )
    # rlp_data = rlp.encode(  rlp.infer_sedes(tx).serialize(tx) )
    # print( hexlify( rlp_data) )
    # print(signed_tx)

    pass


#ERC20-USDT
def  test_transfer_ERC20_USDT():

    #rinkeby 合约地址:  0x0f38e3426de0f7afdf7e641633b287f462f346f2

    erc20_data = make_data(to='0xC4d2e23807d176441221248fCbC03170e40B37d1', value=Decimal('1000001.123456') * (10 ** 6))
    print("erc20_data:{}".format(erc20_data))

    tx = Transaction(nonce=420,
                     gasprice=20 * (10 ** 9),
                     startgas=210000,
                     to='0xeca059f3d6de135e520e789cdfeecbf5ceca3770',
                     value=0,
                     # data=b''
                     data= unhexlify( erc20_data )
                     )
    tx.sender = '0x954d1a58c7abd4ac8ebe05f59191Cf718eb0cB89'
    signed_tx = tx.sign(key='DBBAD2A5682517E4FF095F948F721563231282CA4179AE0DFEA1C76143BA9607',  network_id=None)  # 4:Rinkeby

    rlp_data = rlp.encode(rlp.infer_sedes(signed_tx).serialize(signed_tx))
    print(hexlify(rlp_data))

    pass




if __name__ == '__main__':

    # main()
    # main2()
    # main3()
    # main3_py3()
    test_transfer_ERC20_USDT()
