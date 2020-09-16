#!encoding:utf8

"""
author: yqq
date : 2019-05-12
description: Cosmos区块监测程序, 获取交易交易所用户地址的充币信息
"""

import traceback
import json
import sql
import time
import threading
from time import sleep
from cosmos.cosmos_proxy import  CosmosProxy
from config import USDP_NODE_RPC_HOST 
from config import USDP_NODE_RPC_PORT

#from config import  USDP_N_DEFAULT_START_HEIGHT 
from config import  USDP_N_BLOCK_TO_WAIT_CONFIRM   #区块确认数至少12个
#设置精度 
import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown




#HRC20 地址转换
from binascii import hexlify, unhexlify
from cosmos.my_bech32 import HexAddrToBech32, Bech32AddrToHex

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
#

from config import HRC20_CONTRACT_MAP


class CosmosBlockScanner(CosmosProxy):

    def __init__(self, 
        strNodeIP, 
        nRpcPort , 
        nConfirmBlock, 
        nDefaultStartBlock, 
        strCoinType,
        strTbNameCharge, 
        strTbNameAddress , 
        strTbNameScanStart,
        strTbNameActiveAddrs,
        strTbNamePatchAddrs):
        
        super(CosmosBlockScanner, self).__init__(host=strNodeIP, port= nRpcPort, cointype=strCoinType)


        assert len(strCoinType.strip()) > 0
        assert len(strTbNameCharge.strip()) > 0  and "charge" in strTbNameCharge
        assert len(strTbNameAddress.strip()) > 0  and "accounts" in strTbNameAddress
        assert len(strTbNameScanStart.strip()) > 0  and "t_scan_start" in strTbNameScanStart
        assert len(strTbNameActiveAddrs.strip()) > 0  and "active_addrs" in strTbNameActiveAddrs
        assert len(strTbNamePatchAddrs.strip()) > 0 and "patch_addrs" in strTbNamePatchAddrs
        
        self.__strNodeIP = strNodeIP
        self.__nRpcPort = nRpcPort
        self.__nConfirmBlock = nConfirmBlock
        self.__nDefaultStartBlock = nDefaultStartBlock
        self.__strCoinType = strCoinType.lower()
        self.__strTbNameCharge = strTbNameCharge
        self.__strTbNameAddress = strTbNameAddress
        self.__strTbNameScanStart = strTbNameScanStart
        self.__strTbNameActiveAddrs = strTbNameActiveAddrs
        self.__strTbNamePatchAddrs = strTbNamePatchAddrs
        self.__exUserAddrs = CosmosBlockScanner.GetExchangeUserAddress(self.__strTbNameAddress)
        print("exUserAddrs's size:{}".format(len(self.__exUserAddrs)))


    def __GetMaxBlockNumberFromDB(self):
        try:
            strSql = """select MAX(height) from {};""".format(self.__strTbNameCharge)
            #print(strSql)
            sqlRet = sql.run(strSql)
            #print(sqlRet)
            if isinstance(sqlRet, list) and len(sqlRet) > 0:
                if isinstance(sqlRet[0], dict):
                    strMaxRet = sqlRet[0][u"MAX(height)"]
                    if strMaxRet: return int(str(strMaxRet), 10)
            return 0
        except Exception as e:
            print("GetMaxBlockNumberFromDB() error:" , e)
            return 0 

    def __GetLastestBlockNumberFromBlockChain(self):

        try:
            nLastestBlockNumber = int(str(self.getLastestBlockNumber()))
            return  nLastestBlockNumber
        except Exception as e:
            print("GetLastestBlockNumberFromBlockChain() error:" , e)
            return None


    def __GetTransactionFromBlock(self, nBlockNum : int):
        data = self.getBlockByBlockNum(nBlockNum)
        timeStr = data["block_meta"]["header"]["time"]
        timeStr = timeStr[ : timeStr.rfind('.') ]
        ta = time.strptime(timeStr, "%Y-%m-%dT%H:%M:%S")
        timestamp = int(time.mktime(ta))
        #print("timestamp", timestamp)


        retData = []
        txs = data["block"]["txs"]
        if not isinstance(txs, list): return []
        for tx in txs:
            txData = {}

            #2019-06-13 yqq 因失败的交易也会被打包进区块, 所以,加上交易有效性判断  
            strTxid = str(tx["Hash"]).strip()
            if len(strTxid) != 64:
                print("strTxid is invalid txid")
                continue

            #2020-04-14 增加HRC20交易有效性判断
            if not self.isValidTx(strTxid):
                print("%s is invalid tx" % strTxid)
                continue

            txData["txid"]  = tx["Hash"]
            txData["from"] = tx["From"]
            txData["to"] = tx["To"]
            txData["amount"] = tx["Amount"][0]["amount"]  #单位是 usdp, 不用再除10**8
            txData["timestamp"] = timestamp

            strTxid = txData["txid"].strip()
            strFrom = txData["from"].strip()
            strTo  = txData["to"].strip()

            #print("self.__exUserAddrs size:{}".format(len(self.__exUserAddrs)))
            strLog = "{} is valid tx, from: {} to:{}".format(strTxid, strFrom, strTo)
            if strFrom in self.__exUserAddrs:   #这种情况是地址被归集了,需要更新余额
                self.__RefreshBalanceIntoDB(strFrom)
            if strTo not in self.__exUserAddrs:   #仅监测交易所用户的地址,

                #2020-04-13 增加HRC20判断
                if self.__strCoinType.lower() != 'htdf'  :
                    strLog = strLog + ", but not for exchange."
                    print(strLog)
                    continue

                if strTo not in HRC20_CONTRACT_MAP:
                    strLog = strLog + ", but not for exchange."
                    print(strLog)
                    continue

                #如果是关心的 HRC20 合约交易
                data = tx['Data']

                # 函数签名(4字节)  + 代币接收地址(32字节) + 代币金额(32字节)
                if len(data) != (4 + 32 + 32) * 2:
                    print('data length ')
                    continue

                method_sig = data[ : 4*2]
                if method_sig.lower() != 'a9059cbb':
                    print(f'method sig is not  `transfer` sig . data:{method_sig}')
                    continue

                token_recipient = data[4*2 + 12*2 : 4*2 + 32*2]  #只去最后 20 字节, 去掉全面填补的 0
                recipient_bech32_addr = HexAddrToBech32(hrp='htdf', hexstraddr=token_recipient)

                token_amount = data[4*2 + 32*2 :]
                token_decimal = HRC20_CONTRACT_MAP[strTo]['decimal']
                token_symbol = HRC20_CONTRACT_MAP[strTo]['symbol']

                if  recipient_bech32_addr not in self.__exUserAddrs:
                    print(f'token_recipient bech32_addr {recipient_bech32_addr} is not belong to exchange')

                    #如果源地址是交易所的, 更新 HRC20 代币代币余额
                    if strFrom in self.__exUserAddrs:
                        self.__RefreshHRC20TokenBalance(contract_addr=strFrom, address=recipient_bech32_addr, symbol=token_symbol)

                    continue


                #以防万一
                if not (1 < token_decimal <= 18):
                    print(f' token_decimal is invalid !  {strTo} : {token_decimal} ')
                    continue

                amount = Decimal( int(token_amount, 16))  / Decimal(10**token_decimal)

                if amount < 0.000000001 :
                    print(f' token_amount {token_amount} is too small! skip it!  ')
                    continue

                strfmt_amount = str(RoundDown(amount))

                strsql = """INSERT INTO tb_hrc20_deposit(`txid`,`symbol`,`from`,`to`,`value`,`block_number`,`block_time`,`confirmations`) """
                strsql += f"""VALUES('{tx["Hash"]}', '{token_symbol}', '{strFrom}', '{recipient_bech32_addr}', '{strfmt_amount}', {nBlockNum}, {timestamp}, 10) """
                strsql += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(10)

                print(strsql)

                sqlret  = sql.run(strsql)

                self.__RefreshHRC20TokenBalance(contract_addr=strTo, address=recipient_bech32_addr, symbol=token_symbol)

                continue
            else: # 正常充币的情况
                strLog = strLog + ", it's for exchange."
                self.__RefreshBalanceIntoDB(strTo)
            print(strLog)

            
            retData.append(txData)
        return retData



    #return [{}, {}]
    def __GetTransactionsInfoFromBlock(self, nHeight : int):
        while True:
            try:
                txsRet = []
                print(f'getting latest block ....')
                nChainLastest = self.__GetLastestBlockNumberFromBlockChain()
                print(f'latest block is {nChainLastest}')
                print(f'get block info {nHeight}')
                blockTxs = self.__GetTransactionFromBlock(nHeight)
                print(f'get block {nHeight} finished')
                nConfirmations = nChainLastest - nHeight

                for tx in blockTxs:
                    if not isinstance(tx, dict): continue

                    txTmp = {}

                    txTmp["txid"] = tx["txid"]
                    txTmp["from"] = tx["from"]
                    txTmp["to"] = tx["to"]
                    txTmp["value"] = tx["amount"]
                    txTmp["blocktime"] = tx["timestamp"]
                    txTmp["confirmations"] = nConfirmations
                    txTmp["blockNumber"] = nHeight

                    txsRet.append(txTmp)

                return txsRet
            except Exception as e:
                print(f"GetTransactionsInfoFromBlock({nHeight}) error:{e}")
                sleep(5)  #休眠5秒, 继续试, 防止漏块   2020-02-19
                # return None

    #刷地址余额,方便后期的归集
    def __RefreshBalanceIntoDB(self, strAddr):
        try:
            print("active_addr is : {}".format( strAddr))
            strBalance = self.getBalance(strAddr)  #获取余额
            if Decimal(strBalance) < Decimal("0.00000100"): #余额太小, 从活跃地址表中删除
                strSql = """DELETE FROM {} WHERE address='{}';""".format(self.__strTbNameActiveAddrs, strAddr)
            else:
                strSql = """REPLACE INTO {}(`address`, `balance`) VALUES('{}', {})""".format(self.__strTbNameActiveAddrs, strAddr, strBalance)
            print("sql: {}".format(strSql))
            sqlRet = sql.run(strSql)
        except Exception as e:
            print(" PustActiveAddrIntoDB error:" , e)

    def __RefreshHRC20TokenBalance(self, contract_addr , address, symbol):
        try:
            strbalance = self.getHRC20TokenBalance(contract_addr=contract_addr, address=address)
            strsql = f"""REPLACE INTO tb_hrc20_active_addrs(`symbol`,`address`, `balance`) VALUES('{symbol}', '{address}', {strbalance});"""
            print(strsql)
            sql.run(strsql)
            pass
        except Exception as e:
            print(f'__RefreshHRC20TokenBalance error {str(e)}')
            

    def __PushTxDataIntoDB(self, nHeight, txDatas):
        if not isinstance(nHeight, int):
            print("nHeight is %s, nHeight is not  integer."  % (type(nHeight)) )
            return None

        try:
            jsonTxStr = json.dumps(txDatas)
            #print(jsonTxStr)
            strSql = """REPLACE INTO {}(height, txdata) VALUES({}, '{}')""".format(self.__strTbNameCharge, nHeight, jsonTxStr)
            print(strSql)
            sqlRet = sql.run(strSql)
            return True
        except Exception as e:
            print("PushTxDataIntoDB(nHeight, txDatas):", e)
            return None

    def __GetTxDataFromDB(self, nBegin : int, nEnd : int):

        if not (isinstance(nBegin, int) and (isinstance(nEnd, int) or isinstance(nEnd, int) )):
            print("nBegin or nEnd is not int type.")
            return []

        try:
            txRet = []

            strSql = """SELECT txdata FROM {} WHERE  height >= {} and height <= {};""".format(self.__strTbNameCharge, nBegin, nEnd)
            print(strSql)
            sqlRet = sql.run(strSql)
            #print(sqlRet)
            if not isinstance(sqlRet, list):
                return None
            for item in sqlRet:
                txListStr = item["txdata"]
                txList  = json.loads(txListStr)
                txRet.extend(txList)
            return txRet
        except Exception as e:
            print("GetTxDataInfoDB(nBegin, nEnd):", e)
            return None
        pass

    def __GetScanStartBlock(self, strCoinType):
        """
        从数据库中获取币种的 扫描的起始区块
        """

        #类型判断
        assert (isinstance( strCoinType, str))

        #对参数进行检查
        #注意sql注入
        strType = strCoinType.lower()
        sqlRet = sql.run("""SELECT start_block FROM t_scan_start WHERE coin_type='{0}'""".format(strType))
        if len(sqlRet) > 0 :
            item = sqlRet[0]
            if 'start_block' in item:
                nRet = int(str(item['start_block']), 10)
                return nRet
        return 0




    @staticmethod
    def GetExchangeUserAddress(strTbName):
        sqlRet = sql.run("""SELECT address FROM {0};""".format(strTbName))
        addrs = set()
        for item in sqlRet:
            if 'address' not in item :continue
            addrs.add(item['address'])
        return list(addrs)


    def StartScanBlock(self):

        #线程函数
        def ScanProc(nStart : int, nEnd : int):
            print("scan %d to %d" % (nStart, nEnd))
            n = nStart
            while n < nEnd:
                try:
                    txRet = self.__GetTransactionsInfoFromBlock(n)
                    if (not txRet) or (0 == len(txRet)) : 
                        #print("txRet:", txRet)
                        n += 1
                        continue
                    for iTry in range(10):
                        if self.__PushTxDataIntoDB(n, txRet):
                            print("processed block %d." % (n) )
                            n += 1
                            break   
                except Exception as e:
                    print(e)
                    sleep(0.1)
                    continue

        #userAddrs = self.GetExchangeUserAddress() #获取交易所用户的地址
        #print(userAddrs)

        nMaxHeightDB = self.__nDefaultStartBlock # self.GetMaxBlockNumberFromDB()
        #print("nMaxHeightDB:", nMaxHeightDB)
        nChainLastest = self.__GetLastestBlockNumberFromBlockChain()
        if None == nChainLastest: 
            sleep(15)
            return
    
        nEnd = nChainLastest - self.__nConfirmBlock 

        #获取起始扫描区块高度
        nScanStart = self.__GetScanStartBlock(self.__strCoinType.lower())      

        nStart = nMaxHeightDB
        if 0 == nMaxHeightDB or nMaxHeightDB < nScanStart :
            nStart = nScanStart 

        
        if nStart <= nEnd:
            if nEnd - nStart > 100:
                nEnd = nStart + 20   #分段扫描, 从头扫到尾, 防止太大,中途失败,一直失败
            print("starting scanning , nStart:", nStart, "nEnd:", nEnd)
        else:
            print(" nStart:", nStart, "nEnd:", nEnd)
            sleep(10)
            return
            

        threads = []
        nCount = nEnd - nStart
        nThreadCount = 10
        assert nThreadCount > 0
        if nCount >= 1000:
            print("start 10 threads to scanning.....")
            nAvr = int(nCount // nThreadCount)
            for i in range(nThreadCount):
                if i == nThreadCount - 1: #最后一个线程收尾
                    tmpThread = threading.Thread(target=ScanProc, args=(nStart+i*nAvr, nEnd))
                    threads.append(tmpThread)
                else:
                    tmpThread = threading.Thread(target=ScanProc, args=(nStart+i*nAvr, nStart+i*nAvr+nAvr))
                    threads.append(tmpThread)

            for t in threads:
                sleep(0.1)
                t.start()
            
            for t in threads:
                t.join()

            #保存本次扫描的结束区块高度,翻遍下次获取
            strSql = """UPDATE {} SET start_block={} WHERE coin_type='{}';"""\
                    .format(self.__strTbNameScanStart, nEnd, self.__strCoinType.lower())
            sql.run(strSql)
            sleep(15)
            print("10 threads to scanning over")

            return


            
        # 如果区块少于1000个, 单线程扫描即可
        for n in range(nStart, nEnd):
            txRet = self.__GetTransactionsInfoFromBlock(n)
            if (not txRet) or (0 == len(txRet)) : continue

            for iTry in range(10):
                if self.__PushTxDataIntoDB(n, txRet):
                    break 

        print("scan over. , nStart:", nStart, "nEnd:", nEnd)

        #保存本次扫描的结束区块高度,翻遍下次获取
        strSql = """UPDATE {} SET start_block={} WHERE coin_type='{}';"""\
            .format(self.__strTbNameScanStart, nEnd, self.__strCoinType.lower())

        sql.run(strSql)
        print("sql: {}".format(strSql))
        sleep(1)

        pass

    
    #这是归集查询的patch方案, 用于查询那些老地址的余额
    def PatchForAddrsBalance(self):
        print("-----patch for addrs balance----------")
        strSql = """SELECT DISTINCT address FROM {};""".format(self.__strTbNamePatchAddrs)
        print("sql: {}".format(strSql))
        sqlRet = sql.run(strSql)
        addrs = set()
        for item in sqlRet:
            if 'address' not in item : continue
            addrs.add(item['address'])
        print("patch addrs's length: {}".format(len(addrs)))
        addrs = list(addrs)

        def QueryBalanceProc(addrs):
            for strAddr in addrs:
                strBalance = self.getBalance(strAddr)  #获取余额
                if Decimal(strBalance) > 0.001:
                    strSql = """REPLACE INTO {}(`address`, `balance`) VALUES('{}', {})""".format(self.__strTbNameActiveAddrs, strAddr, strBalance)
                    print("sql: {}".format(strSql))
                    sqlRet = sql.run(strSql)
                else: #金额太小的直接删掉?
                    strSql = """DELETE FROM {} WHERE address='{}'""".format(self.__strTbNameActiveAddrs, strAddr)
                    print("sql: {}".format(strSql))
                    sqlRet = sql.run(strSql)

                strSql = """DELETE FROM {} WHERE address='{}'""".format(self.__strTbNamePatchAddrs, strAddr)
                print("sql: {}".format(strSql))
                sqlRet = sql.run(strSql)
            pass
        
        if len(addrs) < 100:
            #地址数量少于100
            QueryBalanceProc(addrs)
        else: # >= 100  , 启用多线程扫描
            threads = []
            nThreadCount = 10
            print("start 10 threads to scanning.....")
            nAvr = int(len(addrs) // nThreadCount)
            for i in range(nThreadCount):
                if i == nThreadCount - 1: #最后一个线程收尾
                    tmpThread = threading.Thread(target=QueryBalanceProc, args=( addrs[i*nAvr : ] , ))   #注意 (2,) 和 (2)的区别 , 逗号不能少 
                else:
                    tmpThread = threading.Thread(target=QueryBalanceProc, args=( addrs[i*nAvr : i * nAvr + nAvr], ))
                threads.append(tmpThread)

            for t in threads:
                sleep(0.1)
                t.start()
            
            for t in threads:
                t.join()

        print("scanning all patch addresses finished....")
        return



#def main():
#    print("start usdp block scanner.........")
#    #global self.__exUserAddrs 
#    #self.__exUserAddrs = CosmosBlockScanner.GetExchangeUserAddress("t_usdp_accounts")
#    print("len(self.__exUserAddrs):{}".format(len(self.__exUserAddrs)))
#    scanner =  CosmosBlockScanner(USDP_NODE_RPC_HOST, USDP_NODE_RPC_PORT, 0, 0, 
#                        "usdp", "t_usdp_charge", "t_usdp_accounts", "t_scan_start", "t_usdp_active_addrs", "t_usdp_patch_addrs")    
#    while True:
#        try:
#            scanner.PatchForAddrsBalance() #查询patch表用户地址余额
#            scanner.StartScanBlock()
#        except Exception as e:
#            print("error: %s" % str(e))
#            sleep(15)
#    pass


#if __name__ == '__main__':
#    main()

