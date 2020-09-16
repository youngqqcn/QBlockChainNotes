#!encoding:utf8

"""
author: yqq
date : 2019-05-01  
description: 以太坊区块监测程序, 获取交易交易所用户地址的充币信息
"""

import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")



sys.path.append('.')
sys.path.append('..')

import sys
import traceback
from etc.ethproxy import EthProxy
import json
import sql
import time
from time import sleep


# from ethereum.bloom import  *   #使用bloom filter
# from ethereum.bloom import bloom_query

from config import ETC_N_BLOCK_TO_WAIT_CONFIRM     #区块确认数
from config import ETC_NODE_RPC_HOST
from config import ETC_NODE_RPC_PORT
# from config import ERC20_CONTRACTS_LIST   #ERC20合约地址


import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30

from binascii import unhexlify, hexlify

from utils import RoundDown
from utils import hexstr_to_bytes

# Keccak256( tranfer(address,address,uint256) )
# ERC20_TRANSFER_EVENT_HASH = 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

#算法
#0.等待15秒
#1.从数据库中获取最大的区块高度(nMaxHeight)
#2.如果区块高度为0 则从默认(nDefaultStartHeight)的高度开始扫描
#3.如果区块高度不为0, 则从nMaxHeight 开始扫描(包含nMaxHeight)
#4.获取最新区块高度 nLatestHeight 
#5.扫描区块高度 n 的区块内容, 获取 "transactions"字段
#6.遍历"transactions"内容 获取所需信息
#7.n++
#8.如果 n >= nLastestHeight - 12 , 跳至步骤0; 否则跳至步骤5


#N_DEFAULT_START_HEIGHT = 4263637 
#N_BLOCK_TO_WAIT_CONFIRM = 12     #区块确认数至少12个

def hex2Dec(strTmp):
    return int(str(strTmp), 16)

class EthBlockScanner(EthProxy):

    def __init__(self, strEthNodeIP, nEthRpcPort):
        EthProxy.__init__(self, strEthNodeIP, nEthRpcPort)
        self.exUserAddrs = EthBlockScanner.GetExchangeUserAddress()

    @staticmethod
    def GetExchangeUserAddress():
        sqlRet = sql.run('select address from t_eth_accounts;')  #使用ETH地址即可
        addrs = []
        for item in sqlRet:
            if 'address' not in item: continue
            addrs.append(item['address'].strip())
        return addrs

    # def GetMaxBlockNumberFromDB(self):
    #     try:
    #         strSql = """select MAX(height) from t_etc_charge;"""
    #         #print(strSql)
    #         sqlRet = sql.run(strSql)
    #         #print(sqlRet)
    #         if isinstance(sqlRet, list) and len(sqlRet) > 0:
    #             if isinstance(sqlRet[0], dict):
    #                 strMaxRet = sqlRet[0][u"MAX(height)"]
    #                 if strMaxRet: return int(str(strMaxRet), 10)
    #         return 0
    #     except Exception as  e:
    #         print("GetMaxBlockNumberFromDB() error:" , e)
    #         return 0

    def GetLastestBlockNumberFromBlockChain(self):

        try:
            #rpc =  EthProxy("192.168.10.199", 18545)
            nLastestBlockNumber = self.eth_blockNumber()
            return  nLastestBlockNumber 
        except Exception as e:
            print("GetLastestBlockNumberFromBlockChain() error:" , e)
            return None

    
    #return [{}, {}]
    def GetTransactionsInfoFromBlock(self, nHeight ):
        try:

            txRet = []

            nChainLastest = self.GetLastestBlockNumberFromBlockChain()
            if not nChainLastest: return txRet

            blockInfo = self.eth_getBlockByNumber(nHeight)
            if not blockInfo: return txRet

            #使用Bloom Filter 判断是否包含ERC20交易
            # bf =  hex2Dec( blockInfo['logsBloom'] )

            # included_contracts = []
            #测试合约地址是否存在
            # if bloom_query(bf, hexstr_to_bytes(ERC20_TRANSFER_EVENT_HASH)): #检查 transfer事件是否存在
            #     for contract_addr in ERC20_CONTRACTS_LIST:
            #         con_addr = contract_addr.replace('0x', '').lower()  #如果包含'0x'则去掉 '0x'
            #         if bloom_query(bf,   hexstr_to_bytes(con_addr) ):
            #             included_contracts.append(con_addr)

            nTimestamp  = hex2Dec(blockInfo["timestamp"])
            nNumber     = hex2Dec(blockInfo["number"])
            nGasLimit   = hex2Dec(blockInfo["gasLimit"])

            nConfirmations = nChainLastest - nNumber

            for tx in blockInfo["transactions"]:
                txTmp = {}

                #如果是创建合约, to是 null
                if tx['to'] is None: continue

                if tx['to'] in self.exUserAddrs: #普通的ETC充币
                    # 普通的ETC转账
                    txTmp["txid"] = tx["hash"]
                    txTmp["from"] = tx["from"]
                    txTmp["to"] = tx["to"]
                    txTmp["nonce"] = hex2Dec(tx["nonce"])
                    txTmp["blocktime"] = nTimestamp
                    txTmp["confirmations"] = nConfirmations
                    txTmp["blockNumber"] = nNumber
                    txTmp['symbol'] = 'ETC'
                    getcontext().prec = 30
                    txTmp["value"] = "%.8f" % RoundDown(Decimal(hex2Dec(tx["value"])) / Decimal(10 ** 18))  # ether
                    print("found tx:{}".format(txTmp))
                    txRet.append(txTmp)

                else:  #有可能是ERC20代币充值
                    # if 0 == len(included_contracts):
                    #     continue
                    #
                    # #如果是合约调用合约进行的ERC20代币转账, to地址可能并不是代币合约的地址,
                    # #因此必须通过bloomFilter进行过滤, 防止漏掉充值
                    #
                    # receipt = self.eth_getTransactionReceipt(tx['hash'])
                    # if int(receipt['status'], 16) != 1: continue
                    # if len(receipt['logs']) < 1: continue
                    #
                    # bf = hex2Dec(receipt['logsBloom'])
                    # if not bloom_query(bf, unhexlify(ERC20_TRANSFER_EVENT_HASH)):  # 检查 transfer事件是否存在
                    #     # print("transfer event is not in logsBloom.")
                    #     continue
                    #
                    # tmp_con_addrs = []
                    # for contract_addr in ERC20_CONTRACTS_LIST:
                    #     con_addr = contract_addr.replace('0x', '').lower()  # 如果包含'0x'则去掉 '0x'
                    #     if bloom_query(bf, hexstr_to_bytes( con_addr)):
                    #         tmp_con_addrs.append('0x' + con_addr)
                    #         break
                    #
                    # if len(tmp_con_addrs) == 0:
                    #     continue
                    # print("tmp include contract addr : {}".format(tmp_con_addrs))
                    #
                    # # 支持合约的批量转账
                    # for log in receipt['logs']:
                    #     if log['removed']: continue
                    #     topics = log['topics']
                    #
                    #     # transfer事件的topics的数量必须是3
                    #     if len(topics) != 3:
                    #         continue
                    #
                    #     # 如果合约地址不是交易所要监控的合约,则跳过
                    #     if log['address'] not in tmp_con_addrs:
                    #         continue
                    #
                    #     # 如果事件的哈希不是transfer的, 则跳过
                    #     event_hash = topics[0]
                    #     if ERC20_TRANSFER_EVENT_HASH.replace('0x', '').lower() != event_hash.replace('0x', '').lower():
                    #         continue
                    #
                    #     # addr_from 并不完全等于 tx['from'], 即合约的调用者并一定是token的发送方,
                    #     #  可以参考ERC20标准的 transferFrom 方法
                    #     addr_from = '0x' + topics[1][-40:]  # ERC20代币的发送方
                    #     addr_to = '0x' + topics[2][-40:]  # ERC20代币的接收方
                    #
                    #     #如果from地址是交易所的地址(一般是归集操作), 则也需要更新活跃地址表
                    #     if addr_from in self.exUserAddrs:
                    #         strSql = """INSERT INTO t_eth_patch_addrs(`address`) VALUES('{}')""".format(addr_from)
                    #         sqlRet = sql.run(strSql)
                    #
                    #     if addr_to not in self.exUserAddrs:
                    #         print('{} is not exchange address'.format(addr_to))
                    #         continue
                    #
                    #
                    #     # 获取代币简称 , 必须用 log['address'], 不能用tx['to'],
                    #     # 因为合约调用合约, tx['to']是调用者, log['address']才是真正执行的合约
                    #     strSymbol = self.eth_erc20_symbol(log['address'])
                    #     nDecimal = self.eth_erc20_decimals(log['address'])  # 获取小数位数
                    #     strValue = log['data']
                    #
                    #     txTmp["txid"] = tx["hash"]
                    #     txTmp["from"] = addr_from
                    #     txTmp["to"] = addr_to.strip()
                    #     txTmp["nonce"] = hex2Dec(tx["nonce"])
                    #     txTmp["blocktime"] = nTimestamp
                    #     txTmp["confirmations"] = nConfirmations
                    #     txTmp["blockNumber"] = nNumber
                    #     txTmp['symbol'] = strSymbol
                    #
                    #     getcontext().prec = 30
                    #     txTmp["value"] = "%.8f" % RoundDown(Decimal(hex2Dec(strValue)) / Decimal(10 ** nDecimal))  # 单位转换
                    #     print("found tx: {}".format(txTmp))
                    #
                    #     txRet.append(txTmp)
                    pass

            return txRet 
        except Exception as e:
            print("GetTransactionsInfoFromBlock(nHeight) error:" , e)
            return None
        pass



    def PushTxDataIntoDB(self, txDatas):

        try:
            for tx in txDatas:
                strSql = """INSERT INTO tb_etc_series_deposit(`txid`,`symbol`,`from`,`to`,`value`,`block_number`,`block_time`,`nonce`,`confirmations`) """
                strSql += """ VALUES('{}','{}','{}','{}','{}',{},{},{},{})  """\
                            .format( tx['txid'], tx['symbol'], tx['from'], tx['to'], tx['value'], tx['blockNumber'] ,tx['blocktime'], tx['nonce'], tx['confirmations'])
                strSql += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(tx['confirmations'])
                print("sql: {}  ".format(strSql))
                sqlRet = sql.run(strSql)


                #如果 from地址(归集) , 或to地址 属于交易所, 则放入临时表, 下次扫描会更新其余额
                for addr in [tx['from'], tx['to']]:
                    if addr in self.exUserAddrs:
                        strSql = """INSERT INTO t_etc_patch_addrs(`address`) VALUES('{}')""".format( addr )
                        sqlRet = sql.run(strSql)

            return True
        except Exception as e:
            print("PushTxDataIntoDB( txDatas):", e)
            return None

    def GetTxDataFromDB(self, nBegin, nEnd, symbol='ETC'):

        try:
            if not (isinstance(nBegin, int) and (isinstance(nEnd, int) or isinstance(nEnd, int) )):
                print("nBegin or nEnd is not int type.")
                return []

            txRet = []

            # strSql = """SELECT txdata FROM t_etc_charge WHERE  height >= {0} and height <= {1};""".format(nBegin, nEnd)
            strSql = """SELECT * FROM tb_etc_series_deposit  WHERE symbol='{}' and block_number>{} and block_number<{}; """.format(symbol, nBegin, nEnd)
            print("sql  : {}".format(strSql))
            sqlRet = sql.run(strSql)

            if not isinstance(sqlRet, list):
                return None
            for item in sqlRet:
                tx = {}
                tx['symbol'] = item['symbol']
                tx["txid"] = item['txid']
                tx["from"] = item["from"]
                tx["to"] = item["to"]
                tx["nonce"] = item['nonce']
                tx["blocktime"] = item['block_time']
                tx["confirmations"] = item['confirmations']
                tx["blockNumber"] = item['block_number']
                tx["value"] = item['value']
                txRet.append(tx)
            return txRet
        except Exception as e:
            print("GetTxDataInfoDB(nBegin, nEnd, symbol):", e)
            return None
        pass


     #线程函数
    def ScanProc(self, nStart : int, nEnd : int):
        print("scan %d to %d" % (nStart, nEnd))
        for n in range(nStart, nEnd):
            txRet = self.GetTransactionsInfoFromBlock(n )
            if (not txRet) or (0 == len(txRet)) : continue
            #print(txRet)
            for iTry in range(10):
                if self.PushTxDataIntoDB( txRet):
                    break 
        pass

    def __GetScanStartBlock(self, strCoinType):
        """
        从数据库中获取币种的 扫描的起始区块
        """

        #类型判断
        assert (isinstance( strCoinType, str) )

        #对参数进行检查
        #注意sql注入
        strType = strCoinType.lower()
        sqlRet = sql.run("""SELECT start_block FROM t_scan_start WHERE coin_type='{0}';""".format(strType))
        if len(sqlRet) > 0 :
            item = sqlRet[0]
            if 'start_block' in item:
                nRet = int(str(item['start_block']), 10)
                return nRet
        return 0




    def ScanBlock(self):
    
        nMaxHeightDB =  0 #self.GetMaxBlockNumberFromDB()
        print("nMaxHeightDB:", nMaxHeightDB)
        nChainLastest = self.GetLastestBlockNumberFromBlockChain()
        print("nChainLastest:", nChainLastest)
        if not nChainLastest: return

    
        nEnd = nChainLastest - ETC_N_BLOCK_TO_WAIT_CONFIRM


        #获取起始扫描区块高度
        ETC_N_DEFAULT_START_HEIGHT = self.__GetScanStartBlock('etc')

        nStart = nMaxHeightDB
        if 0 == nMaxHeightDB or nMaxHeightDB < ETC_N_DEFAULT_START_HEIGHT :
            nStart = ETC_N_DEFAULT_START_HEIGHT

        if nStart <= nEnd:
            if nEnd - nStart > 1000:  nEnd = nStart + 1000   #分段扫描, 从头扫到尾, 防止太大,中途失败,一直失败
            print("starting scanning , nStart:", nStart, "nEnd:", nEnd)
        else:
            print(" nStart:", nStart, "nEnd:", nEnd)
            return

            
        import threading
        threads = []
        nCount = nEnd - nStart
        nThreadCount = 10
        assert nThreadCount > 0
        if nCount >= 1000:
            print("start 10 threads to scanning.....")
            nAvr = int(nCount // nThreadCount)   #整除  2020-02-26
            for i in range(nThreadCount):
                if i == nThreadCount - 1: #最后一个线程收尾
                    tmpThread = threading.Thread(target=EthBlockScanner.ScanProc, args=(self, nStart+i*nAvr, nEnd ))
                    threads.append(tmpThread)
                else:
                    tmpThread = threading.Thread(target=EthBlockScanner.ScanProc, args=(self, nStart+i*nAvr, nStart+i*nAvr+nAvr ))
                    threads.append(tmpThread)

            for t in threads:
                time.sleep(0.1)
                t.start()
            
            for t in threads:
                t.join()

            #保存本次扫描的结束区块高度,翻遍下次获取
            import sql
            sql.run("""update t_scan_start set start_block={0} where coin_type='{1}'""".format(nEnd, 'etc'))
            print("10 threads to scanning over")
            return



        for n in range(nStart, nEnd):
            txRet = self.GetTransactionsInfoFromBlock(n)

            if (not txRet) or (0 == len(txRet)) : continue

            for iTry in range(10):
                if self.PushTxDataIntoDB( txRet):
                    break

        print("scan over. , nStart:", nStart, "nEnd:", nEnd)

        #保存本次扫描的结束区块高度
        import sql
        strSql = """update t_scan_start set start_block={0} where coin_type='{1}';""".format(nEnd, 'etc')
        sql.run( strSql )
        sleep(15)




    def GetBalanceInEther(self, addr):
        nBalance = self.eth_getBalance(addr, "latest")
        
        #向下取整, 而不是四舍五入, 四舍五入会导致金额偏大
        dBalance =  RoundDown( Decimal(str(nBalance)) / Decimal(str(10**18)) )
        strBalance = '%.8f' % dBalance
        return strBalance


    #这是归集查询的patch方案, 用于查询那些老地址的余额
    def PatchForAddrsBalance(self):
        sqlRet = sql.run('SELECT DISTINCT address FROM t_etc_patch_addrs;')
        addrs = []
        for item in sqlRet:
            if 'address' not in item : continue
            addrs.append(item['address'])

        def QueryBalanceProc(addrs):
            for strAddr in addrs:
                print(type(strAddr))
                strBalance = self.GetBalanceInEther(strAddr)  #获取余额
                if Decimal(strBalance) > 0.001:
                    strSql = """REPLACE INTO tb_etc_series_active_addrs(`symbol`,`address`, `balance`) VALUES('ETC', '{0}', {1})""".format(strAddr, strBalance)
                    print("sql: {}".format(strSql))
                    sqlRet = sql.run(strSql)

                # #检查代币余额
                # for contract_addr in ERC20_CONTRACTS_LIST:
                #     strSymbol = self.eth_erc20_symbol(contract_addr)
                #     strBalance = self.eth_erc20_balanceOf(contract_addr, strAddr, True)
                #     if Decimal(strBalance) > 0.001:
                #         strSql = """REPLACE INTO tb_eth_series_active_addrs(`symbol`,`address`, `balance`) VALUES('{}', '{}', {})""".format(strSymbol, strAddr, strBalance)
                #         print("sql: {}".format(strSql))
                #         sqlRet = sql.run(strSql)
                #     else:
                #         strSql = """DELETE FROM tb_eth_series_active_addrs WHERE `symbol`='{}' and `address`='{}'""".format(strSymbol, strAddr)
                #         print("sql: {}".format(strSql))
                #         sqlRet = sql.run(strSql)

                strSql = """DELETE FROM t_etc_patch_addrs WHERE address='{0}';""".format(strAddr)
                print("sql: {}".format(strSql))
                sqlRet = sql.run(strSql)
            pass
        
        if len(addrs) >= 100:
            import threading
            threads = []
            nThreadCount = 10
            print("start 10 threads to scanning.....")
            nAvr = len(addrs)/ nThreadCount
            for i in range(nThreadCount):
                if i == nThreadCount - 1: #最后一个线程收尾
                    tmpThread = threading.Thread(target=QueryBalanceProc, args=( addrs[i*nAvr : ], ) )
                else:
                    tmpThread = threading.Thread(target=QueryBalanceProc, args=(addrs[i*nAvr : i * nAvr + nAvr], ))
                threads.append(tmpThread)

            for t in threads:
                sleep(0.1)
                t.start()
            
            for t in threads:
                t.join()

            print("scanning all patch addresses finished....")
            return
        
        #地址数量少于100
        QueryBalanceProc(addrs)
        print("scanning all patch addresses finished....")
        return


def main():
    # print("start ethereum block scanner.........")
    # scanner =  EthBlockScanner(ETH_NODE_RPC_HOST , ETH_NODE_RPC_PORT )
    # txs  = scanner.GetTransactionsInfoFromBlock(5040626)
    # return
    # print('------------')

    print("start ethereum-classic block scanner.........")
    scanner =  EthBlockScanner(ETC_NODE_RPC_HOST , ETC_NODE_RPC_PORT ) #不必每次都重新创建对象
    while True:
        try:
            scanner.PatchForAddrsBalance() #查询patch表用户地址余额
            scanner.ScanBlock()
        except Exception as e:
            print("error: %s" % str(e))
            sleep(15)
    pass


if __name__ == '__main__':
    main()

