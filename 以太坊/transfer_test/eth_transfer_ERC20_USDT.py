#!coding:utf8

#author:yqq
#date:2019/8/28 0028 14:22
#description:  ETH 普通转账  /  ERC20 代币转账


#author:yqq
#date:2020/04/17  15:58
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



#ERC20-USDT
def  test_transfer_ERC20_USDT():

    #rinkeby 合约地址:  0x0f38e3426de0f7afdf7e641633b287f462f346f2


    erc20_data = make_data(to='0xC4d2e23807d176441221248fCbC03170e40B37d1', #代币接收地址
                           value=Decimal('1000001.123456') * (10 ** 6))

    print("erc20_data:{}".format(erc20_data))

    tx = Transaction(nonce=420,
                     gasprice=20 * (10 ** 9),
                     startgas=210000,
                     to='0xeca059f3d6de135e520e789cdfeecbf5ceca3770',  #合约地址
                     value=0,
                     # data=b''
                     data= unhexlify( erc20_data )
                     )

    tx.sender = '0x954d1a58c7abd4ac8ebe05f59191Cf718eb0cB89'  #源地址
    signed_tx = tx.sign(key='DBBAD2A5682517E4FF095F948F721563231282CA4179AE0DFEA1C76143BA9607',   #源地址的私钥
                        network_id=None)  # 4:Rinkeby

    rlp_data = rlp.encode(rlp.infer_sedes(signed_tx).serialize(signed_tx))

    print(hexlify(rlp_data)) #交易数据

    pass



if __name__ == '__main__':


    test_transfer_ERC20_USDT()
