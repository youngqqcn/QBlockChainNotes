#!encoding:utf8

"""
author: yqq
date : 2019-05-12
description: USDP区块监测程序, 获取交易交易所用户地址的充币信息
"""


from usdpproxy import USDPProxy
import traceback
import json
import sql
import time
from config import USDP_NODE_RPC_HOST 
from config import USDP_NODE_RPC_PORT

#from config import  USDP_N_DEFAULT_START_HEIGHT 
from config import  USDP_N_BLOCK_TO_WAIT_CONFIRM   #区块确认数至少12个
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



def hex2Dec(strTmp):
    return int(str(strTmp), 16)

class USDPBlockScanner(USDPProxy):

    
    def __init__(self, strNodeIP, nRpcPort):
        USDPProxy.__init__(self, strNodeIP, nRpcPort)

    def GetMaxBlockNumberFromDB(self):
        try:
            strSql = """select MAX(height) from t_usdp_charge;"""
            #print(strSql)
            sqlRet = sql.run(strSql)
            #print(sqlRet)
            if isinstance(sqlRet, list) and len(sqlRet) > 0:
                if isinstance(sqlRet[0], dict):
                    strMaxRet = sqlRet[0][u"MAX(height)"]
                    if strMaxRet: return int(str(strMaxRet), 10)
            return 0 
        except IOError, e:
            print("GetMaxBlockNumberFromDB() error:" , e)
            return 0 

    def GetLastestBlockNumberFromBlockChain(self):

        try:
            nLastestBlockNumber = int(str(self.getLastestBlockNumber()))
            return  nLastestBlockNumber 
        except IOError, e:
            print("GetLastestBlockNumberFromBlockChain() error:" , e)
            return None


    def _getTransactionFromBlock(self, nBlockNum):
        data = self.getBlockByBlockNum(nBlockNum)
        import time
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
            txData["txid"]  = tx["Hash"]
            txData["from"] = tx["From"]
            txData["to"] = tx["To"]
            txData["amount"] = tx["Amount"][0]["amount"]  #单位是 usdp, 不用再除10**8
            txData["timestamp"] = timestamp


            retData.append(txData)
        return retData



    #return [{}, {}]
    def GetTransactionsInfoFromBlock(self, nHeight , userAddrs):
        try:
            txsRet = []

            nChainLastest = self.GetLastestBlockNumberFromBlockChain()
            blockTxs= self._getTransactionFromBlock(nHeight)
            nConfirmations = nChainLastest - nHeight

            for tx in blockTxs:
                if not isinstance(tx, dict): continue

                txTmp = {}   
                if tx["to"] not in userAddrs:   #仅监测交易所用户的地址
                    continue

                txTmp["txid"]   = tx["txid"]
                txTmp["from"]   = tx["from"]
                txTmp["to"]     = tx["to"]
                txTmp["value"]  = tx["amount"]
                txTmp["blocktime"]  = tx["timestamp"]
                txTmp["confirmations"] = nConfirmations
                txTmp["blockNumber"] = nHeight

                txsRet.append( txTmp )

            return txsRet 
        except IOError, e:
            print("GetTransactionsInfoFromBlock(nHeight) error:" , e)
            return None
        pass


    def PushTxDataIntoDB(self, nHeight, txDatas):
        if not isinstance(nHeight, int):
            print("nHeight is %s, nHeight is not  integer."  % (type(nHeight)) )
            return None

        try:
            jsonTxStr = json.dumps(txDatas)
            #print(jsonTxStr)
            strSql = """REPLACE INTO t_usdp_charge(height, txdata) VALUES({0}, '{1}')""".format(nHeight, jsonTxStr)
            #print(strSql)
            sqlRet = sql.run(strSql)
            #print(sqlRet)
            return True
        except IOError, e:
            print("PushTxDataIntoDB(nHeight, txDatas):", e)
            return None

    def GetTxDataFromDB(self, nBegin, nEnd):

        if not (isinstance(nBegin, int) and (isinstance(nEnd, int) or isinstance(nEnd, long) )):
            print("nBegin or nEnd is not int type.")
            return []

        try:
            txRet = []

            strSql = """SELECT txdata FROM t_usdp_charge WHERE  height >= {0} and height <= {1};""".format(nBegin, nEnd)
            #print(strSql)
            sqlRet = sql.run(strSql)
            #print(sqlRet)
            if not isinstance(sqlRet, list):
                return None
            for item in sqlRet:
                txListStr = item["txdata"]
                txList  = json.loads(txListStr)
                txRet.extend(txList)
            return txRet
        except IOError, e:
            print("GetTxDataInfoDB(nBegin, nEnd):", e)
            return None
        pass




    def GetExchangeUserAddress(self):
        sqlRet = sql.run('select address from t_usdp_accounts;')
        addrs = []
        for item in sqlRet:
            if 'address' not in item :continue
            addrs.append(item['address'])
        return addrs 


    #线程函数
    def ScanProc(self, nStart, nEnd, userAddrs):
        print("scan %d to %d" % (nStart, nEnd))
        for n in range(nStart, nEnd):
            txRet = self.GetTransactionsInfoFromBlock(n, userAddrs)
            if (not txRet) or (0 == len(txRet)) : continue
            for iTry in range(10):
                if self.PushTxDataIntoDB(n, txRet):
                    break 

        pass


    def ScanBlock(self):
    
        userAddrs = self.GetExchangeUserAddress() #获取交易所用户的地址
        #print(userAddrs)

        nMaxHeightDB = 0 # self.GetMaxBlockNumberFromDB()
        #print("nMaxHeightDB:", nMaxHeightDB)
        nChainLastest = self.GetLastestBlockNumberFromBlockChain()
    
        nEnd = nChainLastest - USDP_N_BLOCK_TO_WAIT_CONFIRM 

        #获取起始扫描区块高度
        from utils import GetScanStartBlock
        USDP_N_DEFAULT_START_HEIGHT = GetScanStartBlock('usdp')      

        nStart = nMaxHeightDB
        if 0 == nMaxHeightDB or nMaxHeightDB < USDP_N_DEFAULT_START_HEIGHT :
            nStart = USDP_N_DEFAULT_START_HEIGHT 

        if nStart <= nEnd:
            print("starting scanning , nStart:", nStart, "nEnd:", nEnd)
        else:
            print(" nStart:", nStart, "nEnd:", nEnd)
            return
            


        import threading
        threads = []
        nCount = nEnd - nStart
        nThreadCount = 10
        assert nThreadCount > 0
        if nCount > 1000:
            print("start 10 threads to scanning.....")
            nAvr = nCount / nThreadCount
            for i in range(nThreadCount):
                if i == nThreadCount - 1: #最后一个线程收尾
                    tmpThread = threading.Thread(target=USDPBlockScanner.ScanProc, args=(self, nStart+i*nAvr, nEnd, userAddrs))
                    threads.append(tmpThread)
                else:
                    tmpThread = threading.Thread(target=USDPBlockScanner.ScanProc, args=(self, nStart+i*nAvr, nStart+i*nAvr+nAvr, userAddrs))
                    threads.append(tmpThread)
            pass

            for t in threads:
                import time
                time.sleep(1)
                t.start()
            
            for t in threads:
                t.join()

            #保存本次扫描的结束区块高度,翻遍下次获取
            import sql
            sql.run("""update t_scan_start set start_block={0} where coin_type='{1}'""".format(nEnd, 'usdp'))
            print("10 threads to scanning over")

            return


            
        # 如果区块少于1000个, 单线程扫描即可
        for n in range(nStart, nEnd):
        #for n in (nStart, nStart + 1):
            #print('-------start scan block:', n)
            txRet = self.GetTransactionsInfoFromBlock(n, userAddrs)

            #print("------------------txRet-------------------")
            #print(txRet)
            #print("------------------txRet-------------------")
            if (not txRet) or (0 == len(txRet)) : continue

            for iTry in range(10):
                if self.PushTxDataIntoDB(n, txRet):
                    #print("push into db ok.")
                    break 

        print("scan over. , nStart:", nStart, "nEnd:", nEnd)

        #保存本次扫描的结束区块高度,翻遍下次获取
        import sql
        sql.run("""update t_scan_start set start_block={0} where coin_type='{1}'""".format(nEnd, 'usdp'))
        #以下内容,可以作为交易接口 获取数据的参考
        #txRet = self.GetTxDataFromDB(nStart, nStart+1)
        #if not txRet:
        #    print("GetTxDataInfoDB return empty.")
        #    return
        #print("-----------------")
        #print(txRet)
    pass



def main():
    print("start usdp block scanner.........")
    while True:
        try:
            scanner =  USDPBlockScanner(USDP_NODE_RPC_HOST, USDP_NODE_RPC_PORT)
            addrs = scanner.GetExchangeUserAddress()
            scanner.ScanBlock()
            time.sleep(15)
            #break
        except Exception as e:
            traceback.print_exc()
            #print("error: %s" % str(e))
            #break
    pass


if __name__ == '__main__':
    main()

