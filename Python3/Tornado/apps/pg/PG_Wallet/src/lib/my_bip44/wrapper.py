#!coding:utf8

#author:yqq
#date:2020/5/7 0007 18:34
#description: 封装
from src.lib.eth_wallet import Wallet
from src.lib.addr_gen.eth_addr_gen import gen_addr_from_privkey as eth_addr_gen
from src.lib.addr_gen.htdf_addr_gen import gen_addr_from_privkey as htdf_addr_gen
from src.lib.addr_gen.btc_addr_gen import gen_addr_from_privkey as btc_addr_gen

class  Bip44RegNo:
    """
    已经注册BIP44 规范的币种
    https://github.com/satoshilabs/slips/blob/master/slip-0044.md
    """
    BTC     = 0
    HTDF    = 346
    ETH     = 60

    coins = {
        'BTC': BTC,
        'ETH': ETH,
        'HTDF': HTDF
    }



def gen_bip44_subaddr_from_mnemonic(mnemonic : str,
                                   coin_type : str ,
                                   account_index : int ,
                                   address_index : int ,
                                   nettype: str = 'mainnet' ) -> str:
    """
    :param mnemonic: 助记词
    :param coin_type: 币种名
    :param account_index:  子账户索引
    :param address_index: 地址索引
    :param nettype:  mainnet  testnet
    :return:
    """
    tmp_coin_type = coin_type.upper().strip()

    assert  tmp_coin_type in Bip44RegNo.coins

    coin_type_index = Bip44RegNo.coins[tmp_coin_type]


    wallet = Wallet()
    wallet.from_mnemonic(mnemonic=mnemonic)
    addr_path =  f"m/44'/{coin_type_index}'/{account_index}'/0/{address_index}"
    wallet.from_path(addr_path)
    # print( wallet.public_key() )
    # print(wallet.private_key())
    # print( json.dumps( wallet.dumps() , indent=4) )

    priv_key = wallet.private_key()
    if coin_type_index == Bip44RegNo.BTC:
        addr = btc_addr_gen(hex_priv_key=priv_key, nettype=nettype)
    elif coin_type_index == Bip44RegNo.HTDF:
        addr = htdf_addr_gen(priv_key=priv_key)
    elif coin_type_index == Bip44RegNo.ETH:
        addr = eth_addr_gen(priv_key=priv_key)
    else:
        raise Exception("unknown coin type")
    return  addr



def gen_bip44_subprivkey_from_mnemonic(mnemonic : str,
                                   coin_type : str ,
                                   account_index : int ,
                                   address_index : int ) -> str:
    """
    :param mnemonic: 助记词
    :param coin_type: 币种名
    :param account_index:  子账户索引
    :param address_index: 地址索引
    :return:
    """
    tmp_coin_type = coin_type.upper().strip()

    assert  tmp_coin_type in Bip44RegNo.coins

    coin_type_index = Bip44RegNo.coins[tmp_coin_type]

    # func_gen_addr  = htdf_addr_gen if  coin_type_index == Bip44RegNo.HTDF  else eth_addr_gen

    wallet = Wallet()
    wallet.from_mnemonic(mnemonic=mnemonic)
    addr_path =  f"m/44'/{coin_type_index}'/{account_index}'/0/{address_index}"
    wallet.from_path(addr_path)
    # print( wallet.public_key() )
    # print(wallet.private_key())
    # print( json.dumps( wallet.dumps() , indent=4) )
    priv_key = wallet.private_key()

    # addr = func_gen_addr(priv_key=priv_key)
    return  priv_key


def gen_bip44_subaddr_from_seed(seed : str,
                                   coin_type : str ,
                                   account_index : int ,
                                   address_index : int ,
                                    nettype: str = 'mainnet') -> str:
    """
    :param seed: 私钥
    :param coin_type: 币种名
    :param account_index:  子账户索引
    :param address_index: 地址索引
    :return:
    """
    tmp_coin_type = coin_type.upper().strip()

    assert  tmp_coin_type in Bip44RegNo.coins

    coin_type_index = Bip44RegNo.coins[tmp_coin_type]
    # func_gen_addr = htdf_addr_gen if coin_type_index == Bip44RegNo.HTDF else eth_addr_gen

    wallet = Wallet()
    # wallet.from_mnemonic(mnemonic=mnemonic)
    # wallet.from_private_key(private_key=priv_key)
    wallet.from_seed(seed=seed)
    addr_path =  f"m/44'/{coin_type_index}'/{account_index}'/0/{address_index}"
    wallet.from_path(addr_path)
    # print( wallet.public_key() )
    # print(wallet.private_key())
    # print( json.dumps( wallet.dumps() , indent=4) )
    priv_key = wallet.private_key()

    if coin_type_index == Bip44RegNo.BTC:
        addr = btc_addr_gen(hex_priv_key=priv_key, nettype=nettype)
    elif coin_type_index == Bip44RegNo.HTDF:
        addr = htdf_addr_gen(priv_key=priv_key)
    elif coin_type_index == Bip44RegNo.ETH:
        addr = eth_addr_gen(priv_key=priv_key)
    else:
        raise Exception("unknown coin type")
    # addr = func_gen_addr(priv_key=priv_key)
    return  addr



