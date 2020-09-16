#!coding:utf8

#author:yqq
#date:2020/7/10 0010 15:34
#description:  BTC 转账工具类
from typing import Dict
import json

from bitcoin import SelectParams
from bitcoin.core import CMutableTxIn, COutPoint, lx, CScript, Hash160, CMutableTxOut, CMutableTransaction, b2x, COIN
from bitcoin.core.script import OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import SCRIPT_VERIFY_P2SH, VerifyScript
from bitcoin.wallet import CBitcoinSecret, CBitcoinAddress

# from src.consumers.btc.btc_proxy import BTCProxy
from decimal import Decimal

# from src.lib.addr_gen.btc_addr_gen import PrivKeyToWIFCompress
from src.collectors.btc.btc_proxy import BTCProxy
from src.lib.addr_gen.btc_addr_gen import PrivKeyToWIFCompress
from src.lib.log import get_default_logger
from src.lib.pg_utils import round_down, decimal_default
from collections import OrderedDict

MIN_AVAILABLE_UTXO_VALUE_IN_SATOSHI = 10000

class BTCTransferUitl(BTCProxy):

    def __init__(self, host: str, port: int, net_type: str = 'mainnet'):
        assert  net_type in ['testnet', 'mainnet', 'regtest'], f'invalid net_type {net_type}'
        self.net_type = net_type
        self.logger = get_default_logger()
        super().__init__(host=host, port=port)
        pass

    def search_utxo(self, addrs: list,  total_amount: Decimal,
                    min_utxo_value:int = MIN_AVAILABLE_UTXO_VALUE_IN_SATOSHI ) -> (bool, Dict, int):

        ret_utxos_map = dict()
        sum = Decimal(0)
        sum_satoshi = 0
        is_enough = False
        for addr in addrs :
            if is_enough: break
            utxos = self.get_utxo(address=addr, include_mem=True)

            utxos.sort(key=lambda item: item['value'], reverse=False) #按照金额升序排序
            utxos.sort(key=lambda item: item['status']['confirmed'], reverse=True) #按照确认状态排序, 已确认的靠前

            for utxo in utxos:
                value_in_satoshi = utxo['value']
                if value_in_satoshi < min_utxo_value: continue   #金额太小, 不要
                sum += round_down(Decimal(value_in_satoshi) / Decimal(10 ** 8))

                sum_satoshi += value_in_satoshi

                if addr not in ret_utxos_map: ret_utxos_map[addr] = []
                ret_utxos_map[addr].append(utxo)
                if sum >= total_amount:
                    is_enough = True
                    break

        return is_enough, ret_utxos_map, sum_satoshi



    def transfer(self, src_addrs_key_map: OrderedDict, dst_addrs_amount_map: dict ,
                 txfee: Decimal , auto_calc_pay_back: bool, pay_back_index: int = 0xfffffff,
                 ensure_one_txout: bool = False) -> str:
        """

        :param src_addrs_key_map: {'addr1': 'privkey1', 'addr2': 'privkey2'  }   私钥为  hex字符串
        :param dst_addrs_amount_map: {'addr1':Decimal(0.1234), 'addr2':Deciaml(0.234) }
        :param txfee:  矿工费
        :param auto_calc_pay_back: 是否自动计算并找零
        :param pay_back_index: 找零地址索引  即在 src_addrs_key_map 中的索引
        :param ensure_one_txout:   确认只有一个交易输出(比如: 提币不需要找零的情况, 归集)
        :return: txid
        """
        #仅支持 P2PKH 类型的from地址

        assert isinstance(src_addrs_key_map, OrderedDict) , 'src_addrs_key_map is not OrderedDict'
        assert isinstance(dst_addrs_amount_map, dict), 'dst_addrs_amount_map is not dict'
        assert Decimal('0.00001') <= txfee <= Decimal('0.001'),  'invalid txfee, please check txfee'
        assert  len(src_addrs_key_map) >= 1, 'src_addrs_key_map length must >= 1'
        assert  not (True == auto_calc_pay_back  == ensure_one_txout) , \
                'True == auto_calc_pay_back  == ensure_one_txout , must be mutex '

        if ensure_one_txout:
            assert  (len(dst_addrs_amount_map) == 1 ), 'dst_addrs_amount_map length must equal 1'
        elif not auto_calc_pay_back:
            assert  (len(dst_addrs_amount_map) >= 1 ), 'dst_addrs_amount_map length must >= 2'

        if auto_calc_pay_back and pay_back_index >= len(src_addrs_key_map):
            raise Exception('pay_back_index is to large')

        self.logger.info(f'dst_addrs_amount_map is { json.dumps(dst_addrs_amount_map, indent=4, default=decimal_default) }')


        total_amount = sum(dst_addrs_amount_map.values()) + txfee
        self.logger.info(f'total_amount is {total_amount}')

        source_addrs = list(src_addrs_key_map.keys())  #WARNING: 禁止打印私钥!!!

        is_enough, founded_utxos, sum_satoshi = self.search_utxo(addrs=source_addrs, total_amount=total_amount)
        if not is_enough:
            msg = 'balance is not enough'
            self.logger.error(msg)
            raise  Exception(msg)


        self.logger.info(f'founded_utxos is { json.dumps(founded_utxos, indent=4, default=decimal_default) }')


        #设置全局变量
        SelectParams(self.net_type)

        #构造inputs
        txins = []
        utxo_owner_map = dict()
        for addr , utxos in founded_utxos.items():

            assert  addr in src_addrs_key_map , 'addr is not in src_addrs_key_map'

            for utxo in utxos:
                txin = CMutableTxIn(prevout=COutPoint(hash=lx(utxo['txid']), n=utxo['vout']))
                txins.append(txin)

                #因为顺序不会被打乱, 所以可以直接使用 索引进行对应
                utxo_owner_map[len(txins) - 1] = addr

        #构造outputs
        txouts = []
        for to_addr , amount in dst_addrs_amount_map.items():
            out = CMutableTxOut(nValue=amount * COIN, scriptPubKey=CBitcoinAddress(to_addr).to_scriptPubKey())
            txouts.append(out)

        #自动结算
        if auto_calc_pay_back:
            sum_in_satoshi = 0
            for addr, utxos in founded_utxos.items():
                for utxo in utxos:
                    sum_in_satoshi += utxo['value']
            pay_back_in_satoshi = int(sum_in_satoshi - int(total_amount * COIN) )

            if pay_back_in_satoshi >= MIN_AVAILABLE_UTXO_VALUE_IN_SATOSHI:
                pay_back_addr = list(src_addrs_key_map.keys())[pay_back_index]
                pay_back_out = CMutableTxOut(nValue=pay_back_in_satoshi,
                                             scriptPubKey=CBitcoinAddress(pay_back_addr).to_scriptPubKey())
                txouts.append(pay_back_out)


        muttx  = CMutableTransaction(vin=txins, vout=txouts)

        #对每个 input 进行签名
        for n in range(len(txins)):

            #查找这个utxo属于哪个地址
            owner_addr = utxo_owner_map[n]
            privkey =  src_addrs_key_map[owner_addr]

            if len(privkey) == 64: # hex
                wif_key = PrivKeyToWIFCompress(privkey, self.net_type != 'mainnet')
                seckey = CBitcoinSecret(s = wif_key)
            elif len(privkey) == 52:   #base58格式
                seckey = CBitcoinSecret(s = privkey)
            else:
                raise Exception("invalid privkey")

            txin_script_pubkey = CScript([OP_DUP, OP_HASH160, Hash160(seckey.pub), OP_EQUALVERIFY, OP_CHECKSIG])
            sig_hash = SignatureHash(txin_script_pubkey, muttx, n, SIGHASH_ALL)
            sig = seckey.sign(sig_hash) + bytes([SIGHASH_ALL])
            muttx.vin[n].scriptSig = CScript([sig, seckey.pub])

            #TODO: 处理验签失败抛异常
            VerifyScript(muttx.vin[n].scriptSig, txin_script_pubkey, muttx, n, (SCRIPT_VERIFY_P2SH,))
            pass

        raw_tx_hex = b2x(muttx.serialize())
        self.logger.info(f'raw_tx_hex is: {raw_tx_hex}')

        # local_tx_hash = muttx.GetTxid()
        # self.logger.info(f'local_tx_hash is: {b2x(local_tx_hash)}')

        #广播交易
        assert self.ping() == True, 'bitcoind rpc is gone'  # 测试 bitcoind的 rpc服务是否还在
        txid  = self.send_raw_tx(raw_tx_hex=raw_tx_hex)
        self.logger.info(f'send_raw_tx txid is: {txid}')

        return txid


def foo1():

    btcutil = BTCTransferUitl(host='192.168.10.199', port=3002, net_type='regtest')


    src_addr_key_map = OrderedDict()
    src_addr_key_map['moAt6v6gpfJhSBYSmS2AzanW9565kakujW'] = '8baadf3faf9b7f8df9089d550abd75ef33ec7d02469f8ff4169f1b31f0b60b98'
    # {
    #     'moAt6v6gpfJhSBYSmS2AzanW9565kakujW' : 'cSGCNnp3LxnRHaQnjrs3mRRX8wrSdeck5oDz51MhTyMx1mikrQKd',
        # 'moAt6v6gpfJhSBYSmS2AzanW9565kakujW' : '8baadf3faf9b7f8df9089d550abd75ef33ec7d02469f8ff4169f1b31f0b60b98',
    # }

    dst_addr_amount_map = {
        'n4EUHxfnu1jvPRbqm9G7VTheH8WVYStUdm' : Decimal('100.0666'),
        'mmNJuiQK4U4VEUcR3WCjmFD9UCEYHDw9jt' : Decimal('0.1234'),
        'n2iwTm5cT7PCYQ4ymoFD5kycHMoV2Ab8TB' : Decimal('0.99999999'),
        '2N11UaUuvA8dUVTPhCkUqP7yVtVsPQXv6Q1': Decimal('0.876543211')
    }
    txfee = Decimal('0.0001')


    txid = btcutil.transfer(src_addrs_key_map=src_addr_key_map,
                     dst_addrs_amount_map=dst_addr_amount_map,
                     txfee=txfee,
                     auto_calc_pay_back=True,
                     pay_back_index=0,
                     ensure_one_txout=False)
    # 75988ed243ae7d99c4d5eae632449418e36a9105cfdd5c46e6a1cd453b30b8ba
    print(txid)


    pass


def foo2():
    btcutil = BTCTransferUitl(host='192.168.10.199', port=3002, net_type='regtest')

    src_addr_key_map = {
        # 'moAt6v6gpfJhSBYSmS2AzanW9565kakujW' : 'cSGCNnp3LxnRHaQnjrs3mRRX8wrSdeck5oDz51MhTyMx1mikrQKd',
        'moAt6v6gpfJhSBYSmS2AzanW9565kakujW': '8baadf3faf9b7f8df9089d550abd75ef33ec7d02469f8ff4169f1b31f0b60b98',
        'mjGRnCSyan333FdQVKonTFTmNqESaHUJmt': 'cVNHD7FCKEpm3yafwNjusAjz1oqm9e2nHpQJzhmHyCMZLbckCNbg',
    }

    src_addr_key_map = OrderedDict()
    src_addr_key_map['moAt6v6gpfJhSBYSmS2AzanW9565kakujW'] = '8baadf3faf9b7f8df9089d550abd75ef33ec7d02469f8ff4169f1b31f0b60b98'
    src_addr_key_map['mjGRnCSyan333FdQVKonTFTmNqESaHUJmt'] = 'cVNHD7FCKEpm3yafwNjusAjz1oqm9e2nHpQJzhmHyCMZLbckCNbg'



    dst_addr_amount_map = {
        'n4EUHxfnu1jvPRbqm9G7VTheH8WVYStUdm': Decimal('100.0666'),
        'mmNJuiQK4U4VEUcR3WCjmFD9UCEYHDw9jt': Decimal('0.1234'),
        'n2iwTm5cT7PCYQ4ymoFD5kycHMoV2Ab8TB': Decimal('0.99999999'),
        # '2N11UaUuvA8dUVTPhCkUqP7yVtVsPQXv6Q1': Decimal('100.876543211'),
        # 'moAt6v6gpfJhSBYSmS2AzanW9565kakujW': Decimal('0.123')
    }
    txfee = Decimal('0.0001')

    txid = btcutil.transfer(src_addrs_key_map=src_addr_key_map,
                            dst_addrs_amount_map=dst_addr_amount_map,
                            txfee=txfee,
                            auto_calc_pay_back=True,
                            pay_back_index=0,  #指定找零地址
                            ensure_one_txout=False)
    # 75988ed243ae7d99c4d5eae632449418e36a9105cfdd5c46e6a1cd453b30b8ba
    print(txid)
    pass



def main():
    # foo1()
    foo2()

    pass

if __name__ == '__main__':
    main()