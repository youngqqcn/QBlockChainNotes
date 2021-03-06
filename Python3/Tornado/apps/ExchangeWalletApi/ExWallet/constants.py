# coding:utf8
# !/usr/bin/python

#####################################################################################################
# MySQL Info ########################################################################################
#####################################################################################################
import os

# SQL_IP_ADDR, SQL_PORT = '127.0.0.1', 3306
SQL_IP_ADDR, SQL_PORT = '192.168.10.174', 3306
SQL_USRNAME = 'root'
# SQL_PASSWD = os.environ.get('SQL_PWD')
SQL_PASSWD = 'eWFuZ3FpbmdxaW5n'
DBNAME = 'wallet'

#####################################################################################################
# Http Connection Info###############################################################################
#####################################################################################################

WALLET_API_PORT = 9000

#####################################################################################################
# RPC Info###########################################################################################
#####################################################################################################
# Bitcoin Family
### BTC
BTC_IP_ADDR = '192.168.10.199'
BTC_RPC_USERNAME = 'btc'
BTC_RPC_PASSWD = 'btc2018'
BTC_RPC_PORT = 18332
BTC_RPC_URL = "http://%s:%s@%s:%d" % (BTC_RPC_USERNAME, BTC_RPC_PASSWD, BTC_IP_ADDR, BTC_RPC_PORT)

### USDT(OMNI)
OMNI_IP_ADDR = '192.168.10.200'
OMNI_RPC_USERNAME = 'btc'
OMNI_RPC_PASSWD = 'btc2018'
OMNI_RPC_PORT = 18332
OMNI_RPC_URL = "http://%s:%s@%s:%d" % (OMNI_RPC_USERNAME, OMNI_RPC_PASSWD, OMNI_IP_ADDR, OMNI_RPC_PORT)

# Ethereum Family
### ETH
ETH_IP_ADDR = '192.168.10.199'
ETH_RPC_PORT = 18545


### ETC  测试环境也使用Rinkeby
ETC_IP_ADDR = '192.168.10.199'
ETC_RPC_PORT = 18545



########## BlackList #############################
URL_BLACK_LIST = 'http://test-system.htdfscan.com/api/monitor'
USER_HASH = '8a09aeab4b41ab7bf43644d1c1ae887a'
WHITE_LIST = [
    "htdf1ll9vc32wggxmh7enl2vggry0e4u3f5knmvq2d6",
    "htdf1m5phsvgrwpxdsmah5cqkvd6ffz9xzrc3e0jkr2",
    "htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2",
]
###################################################


########### ERC20 Contract #################


ERC20_CONTRACTS_MAP = {
    "BJC": "0x9aa64145f63678756db7be37a34017e09394090b",  # BJC Test
    "YQB": "0x130fc2749d35fe026f32427f60dd3f2ecb6c2f33",  # YQB test
    "MBJC": "0x92ae9a4a93018477e4fbe3eea921c9e1b5338215",  # MBJC Test
    "BNB": "0xe30d2b6f144e6ead802414c09a3f519b72ff12f3",  # BNB  Test
    "LEO": "0x5a2cbd017beeed9983bbc94ce8898bd7764db916",  # LEO  test
    "HT": "0xd8f102e3a9ef15099daaac1481ee262ee5515d87",  # HT test
    "BEI": "0xcc4ec193ef87a5b02a25f3d8fc0fdeacf3255ca9",  # BEI test
    "SPQQ": "0xa5b9b49a50ed529de97d57b320355eb0a71f68d2",  # SPQQ test
    "ECNY": "0xc2f4df10e7fcde92df821ae12569824316381a86",  # ECNY test
    "LINK": "0xA73a509456CeEA0a4E82Dc38F6FB480c48bAadB0",  # LINK test 18
    "ZIL": "0x3cDB7ef06726a5c530Bd9b05b748481528fe1720",  # ZIL test 12
    "ELF": "0x7c220fdDfec15b60D5b35012784c99c9eA61ce7E",  # ELF test 18
    "XMX": "0xf78f5bAe94CA84023177c1c0fa7128672069EB0D",  # XMX test 8
    "TNB": "0x65BDB39Ec96Af430041fD1232bD67590f52c7433",  # TNB test 18

    "USDT": "0xEca059F3d6De135E520E789CDfEeCBf5CECa3770",  # ERC20-USDT test
    "OMG": "0x34db9c9127f523e1bfc5d4e5bd1f0a679d7317c2",  # OMG test
    "MKR": "0xeE6712Ac79954c165e9A2f9C9d4533dd43FC2828",  # MKR test
    "LOOM": "0x297B89C58Beb30291dE98a746e58D6E6BDE54Da9",  # LOOM test
    "MCO": "0xf6971E7E0af35aB1Ae773C391D13dc173c783a1B",  # MCO test
    "CVC": "0xb28964D3191988b7c5a1edAfD58c74C815617bc1",  # CVC test
    "REP": "0x6527Fe1Eb1ad971c0a816d5A558C99cD49f00418",  # REP test
    "CTXC": "0x489cb65f6e8B4093762079E8980495CE349bF9E0",  # CTXC test
    "ABT": "0x0698424f88F0f52F386F2562F57dEC8f3a1D12Cb",  # ABT test
    "PPT": "0xE8a4Bc84EbdE4912BAae28C58f9c95EEed000617",  # PPT test
    "FSN": "0x6deC13A6E7d90Ff6eC26aA2740272aB93D8278C7",  # FSN test
    "REQ": "0x685CdE0e8eb60100E8F0E0b2889483298731132a",  # REQ test
    "TNT": "0x167C507DaFDcB37A30232635d3995c6841043f5D",  # TNT test

    "LILY": "0xd2eab29c836C35C39C42776a612134c1Dc81df96",  # LILY test  18
    "EUTD": "0x2Ad350664F1e195a7e248Da8688fBa7043838A78",  # EUTD  test  18
}
ERC20_CONTRACTS_LIST = ERC20_CONTRACTS_MAP.values()

##########################################


### LTC
LTC_IP_ADDR = '192.168.10.200'
LTC_RPC_USERNAME = 'ltc'
LTC_RPC_PASSWD = 'ltc2018'
LTC_RPC_PORT = 18089
LTC_RPC_URL = "http://%s:%s@%s:%d" % (LTC_RPC_USERNAME, LTC_RPC_PASSWD, LTC_IP_ADDR, LTC_RPC_PORT)

### BSV
BSV_IP_ADDR = '192.168.10.161'
BSV_RPC_USERNAME = 'bsv'
BSV_RPC_PASSWD = 'bsv2018'
BSV_RPC_PORT = 18332
BSV_RPC_URL = "http://%s:%s@%s:%d" % (BSV_RPC_USERNAME, BSV_RPC_PASSWD, BSV_IP_ADDR, BSV_RPC_PORT)

### BCH
BCH_IP_ADDR = '192.168.10.159'
BCH_RPC_USERNAME = 'bch'
BCH_RPC_PASSWD = 'bch2018'
BCH_RPC_PORT = 18332
BCH_RPC_URL = "http://%s:%s@%s:%d" % (BCH_RPC_USERNAME, BCH_RPC_PASSWD, BCH_IP_ADDR, BCH_RPC_PORT)

### DASH
DASH_IP_ADDR = '192.168.10.200'
DASH_RPC_USERNAME = 'dash'
DASH_RPC_PASSWD = 'dash2018'
DASH_RPC_PORT = 19998
DASH_RPC_URL = "http://%s:%s@%s:%d" % (DASH_RPC_USERNAME, DASH_RPC_PASSWD, DASH_IP_ADDR, DASH_RPC_PORT)

# USDP
# USDP_IP_ADDR = '47.99.81.158'
USDP_IP_ADDR = '47.98.241.77'
# USDP_IP_ADDR = '192.168.10.23'
USDP_RPC_PORT = 1317

# HTDF_2020
# 节点名称	域名：端口
# TEST-HTDF-No1	120.77.170.207:1317  深圳
# TEST-HTDF-No2	123.56.71.141:1317   北京
# TEST-HTDF-No3	47.111.137.51:1317   杭州
# TEST-HTDF-No4	47.104.255.242:1317   青岛

HTDF_IP_ADDR = 'htdf2020-test01.orientwalt.cn'
HTDF_RPC_PORT = 1317

HRC20_CONTRACT_MAP = {
    #例如: "contract_addr" : { "decimal": 精度, "symbol":"AJC"  }
    #"htdf1nkkc48lfchy92ahg50akj2384v4yfqpm4hsq6y":{ "decimal": 18, "symbol":"AJC"  },
    "htdf1y2tmw3aa65dvlgcpsz2pd9vqyz3587vncjlmld":{ "decimal": 18, "symbol":"HFH"  },
    #"htdf12dvguqedrvgfrdl35hcgfmz4fz6rm6chrvf96g":{ "decimal": 18, "symbol":"BWC"  },


    #"htdf178qsds3kzu37zlpd2ff7gulmk4z2gupwd8qm3p":{ "decimal": 18, "symbol":"HET"  },
    #"htdf1ahm5zclt52pd58msy9vdtd5059f8cukwlkcwnm":{ "decimal": 18, "symbol":"USDP"  },
    #"htdf1djt7ffg4pdlma7q70v7c4vx4h7uukl7e5y4rvf":{ "decimal": 18, "symbol":"BEI"  },
    #"htdf1lnn5k8p080dyhmtkcrd6936yd86um4g6r5ms46":{ "decimal": 18, "symbol":"AQC"  },
    #"htdf1hpvz7jl0mvtpjc4hs4gku858gj47q6nva606jc":{ "decimal": 18, "symbol":"SJC"  },

   "htdf1vw4dq4teurls7yg8254pz5esn0gpg0492yvt95" : { "decimal": 18, "symbol":"BTU"  },
   "htdf19cwnd3xwnlcce56cjd848d42xsp8gcg5fsm7pa" : { "decimal": 18, "symbol":"SVU"  },
   "htdf132atpl4xs9hd5qhjctyhtsc70nzanv6vmlagzq" : { "decimal": 18, "symbol":"BKL"  },

   "htdf1ywr835q6n03jv0th47l6k6qjv93nvlygkcxjnf" : { "decimal": 18, "symbol":"JXC"  },

    #2020-08-04 新增
    "htdf1jacum30uyygdk0lr483nzg4xfk6l276966ugtk" : { "decimal": 18, "symbol":"AGG"  },
    "htdf18d6eeve6a2p06mn55wf957r476udhw6utq6x8v" : { "decimal": 18, "symbol":"HHG"  },

    #2020-08-20
	"htdf1pn5kxnekyns4mneuzylyka3fyhz9hnppdruwt4" : {"decimal":18, "symbol":"HTD"},
	"htdf1d5na3tf0pun72mmprl2ezdn72lv4uzm64nsmj0" : {"decimal":18, "symbol":"KML"},
	"htdf19xzu8pnkryfmww3l5z4mcmll9qxnt8dla0yyn3" : {"decimal":18, "symbol":"MSL"},
	"htdf1fx09nq997app7knaztm75tddm73vwwc8l66kye" : {"decimal":18, "symbol":"DFQ"},
	"htdf1hkqxrp2w3222edgv3g535exzfw2yls7qm5dmxv" : {"decimal":18, "symbol":"TTB"},
}

# HET
HET_IP_ADDR = "47.106.197.255"  # 深圳, 阿里云
HET_RPC_PORT = 1317


# XRP
# XRP_RIPPLED_PUBLIC_API_URL = 'https://s.altnet.rippletest.net:51234/'
XRP_RIPPLED_PUBLIC_API_URL = 's.altnet.rippletest.net'
XRP_RIPPLED_PUBLIC_API_PORT = 51234



######### EOS ##########################
# EOS   testnet
EOS_PUBLIC_API_URL = 'http://jungle2.cryptolions.io:80'
#备用1(测试环境): 'https://api.jungle.alohaeos.com'
#########################################


########## XLM ################
XLM_RPC_HOST = "https://horizon-testnet.stellar.org"   #testnet

############################




#########  XMR #################
XMR_PRIV_VIEW_KEY = '53a60fee1ef4386838cf7d7c5e0b5a252287590fc544a3fda802e92cce3a880a'
XMR_MASTER_ADDR = '56Trp8Gc9x5M5mLhxMqUaz5AuQpobGfHScyQKGMMmnZFcSFTj6zJFNDUGyDR5SVadjAmxgBp8qv1u2vZsEs8Vo1T4qqrFaa'

XMR_RPC_HTTPS_ENABLE = True
XMR_WALLET_RPC_HOST = '192.168.10.160'
XMR_WALLET_RPC_PORT_AUTO =  58089
XMR_WALLET_RPC_PORT_MANUAL =  58088
###################################


HTTP_TIMEOUT_SECS = 20

#####################################################################################################
# Ethereum###########################################################################################
#####################################################################################################
BLOCK_TAG_EARLIEST = 'earliest'
BLOCK_TAG_LATEST = 'latest'
BLOCK_TAG_PENDING = 'pending'
BLOCK_TAGS = (
    BLOCK_TAG_EARLIEST,
    BLOCK_TAG_LATEST,
    BLOCK_TAG_PENDING,
)
ETH_BLK_BUFFER_SIZE = 30
#####################################################################################################
# OMNI ##############################################################################################
#####################################################################################################
OMNI_PROPERTY_ID = 2  # Test: 2, Tether: 31
OMNI_TRANSACTION_FEE = '0.00006'  # 0.00000257
OMNI_TRANSACTION_RECIPIENT_GAIN = 0.00000546

if __name__ == "__main__":
    pass
