#!encoding:utf8


from ethproxy import EthProxy
import json

#from sql import run
import sql
import time


#0.等待15秒
#1.从数据库中获取最大的区块高度(nMaxHeight)
#2.如果区块高度为0 则从默认(nDefaultStartHeight)的高度开始扫描
#3.如果区块高度不为0, 则从nMaxHeight 开始扫描(包含nMaxHeight)
#4.获取最新区块高度 nLatestHeight 
#5.扫描区块高度 n 的区块内容, 获取 "transactions"字段
#6.遍历"transactions"内容 获取所需信息
#7.n++
#8.如果 n >= nLastestHeight - 12 , 跳至步骤0; 否则跳至步骤5


#return int


N_DEFAULT_START_HEIGHT = 4263637
N_BLOCK_TO_WAIT_CONFIRM = 12     #区块确认数至少12个

def hex2Dec(strTmp):
    return int(str(strTmp), 16)

def GetMaxBlockNumberFromDB():
    try:
        strSql = """select MAX(height) from t_eth_charge;"""
        print(strSql)
        sqlRet = sql.run(strSql)
        print(sqlRet)
        if isinstance(sqlRet, list) and len(sqlRet) > 0:
            if isinstance(sqlRet[0], dict):
                strMaxRet = sqlRet[0][u"MAX(height)"]
                if strMaxRet: return int(str(strMaxRet), 10)
        return 0 
    except IOError, e:
        print("GetMaxBlockNumberFromDB() error:" , e)
        return 0 

def GetLastestBlockNumberFromBlockChain():

    try:
        rpc =  EthProxy("192.168.10.199", 18545)
        nLastestBlockNumber = rpc.eth_blockNumber()
        return  nLastestBlockNumber 
    except IOError, e:
        print("GetLastestBlockNumberFromBlockChain() error:" , e)
        return None



#return [{}, {}]
def GetTransactionsInfoFromBlock(nHeight , userAddrs):
    try:
        txRet = []

        nChainLastest = GetLastestBlockNumberFromBlockChain()

        rpc =  EthProxy("192.168.10.199", 18545)
        blockInfo = rpc.eth_getBlockByNumber(nHeight)
        
        nTimestamp  = hex2Dec(blockInfo["timestamp"])
        nNumber     = hex2Dec(blockInfo["number"])
        nGasLimit   = hex2Dec(blockInfo["gasLimit"])

        nConfirmations = nChainLastest - nNumber

        for tx in blockInfo["transactions"]:
            txTmp = {}   
            if tx["to"] not in userAddrs:   #仅监测交易所用户的地址
                continue

            txTmp["txid"]   = tx["hash"]
            txTmp["from"]   = tx["from"]
            txTmp["to"]     = tx["to"]
            txTmp["value"]  = hex2Dec(tx["value"])
            txTmp["gas"]    = hex2Dec(tx["gas"])
            txTmp["gasLimit"]   = nGasLimit
            txTmp["nonce"]      = hex2Dec(tx["nonce"])
            txTmp["blocktime"]  = nTimestamp
            txTmp["confirmations"] = nConfirmations
            #txTmp["input"] = tx["input"]   # 对于ERC20的代币,input是调用智能合约的关键

            txRet.append( txTmp )

        return txRet 
    except IOError, e:
        print("GetTransactionsInfoFromBlock(nHeight) error:" , e)
        return None
    pass


def PushTxDataIntoDB(nHeight, txDatas):

    try:
        jsonTxStr = json.dumps(txDatas)
        #print(jsonTxStr)
        strSql = """REPLACE INTO t_eth_charge(height, txdata) VALUES({0}, '{1}')""".format(nHeight, jsonTxStr)
        #print(strSql)
        sqlRet = sql.run(strSql)
        #print(sqlRet)
        return True
    except IOError, e:
        print("PushTxDataIntoDB(nHeight, txDatas):", e)
        return None

def GetTxDataFromDB(nBegin, nEnd):

    try:
        txRet = []

        strSql = """SELECT txdata FROM t_eth_charge WHERE  height >= {0} and height <= {1};""".format(nBegin, nEnd)
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

    pass




def GetExchangeUserAddress():
    sqlRet = sql.run('select address from t_eth_accounts;')
    addrs = []
    for item in sqlRet:
        if 'address' not in item :continue
        addrs.append(item['address'])
    return addrs 



def ScanBlock():
    
    userAddrs = GetExchangeUserAddress() #获取交易所用户的地址

    nMaxHeightDB =  GetMaxBlockNumberFromDB()
    print("nMaxHeightDB:", nMaxHeightDB)
    #nMaxHeightDB = 0# GetMaxBlockNumberFromDB()
    nChainLastest = GetLastestBlockNumberFromBlockChain()
    
    nEnd = nChainLastest - N_BLOCK_TO_WAIT_CONFIRM 


    nStart = nMaxHeightDB
    if 0 == nMaxHeightDB or nMaxHeightDB < N_DEFAULT_START_HEIGHT :
        nStart = N_DEFAULT_START_HEIGHT 

    for n in (nStart, nEnd)
    #for n in (nStart, nStart + 1):
        print('-------start scan block:', n)
        txRet = GetTransactionsInfoFromBlock(n, userAddrs)

        #print("------------------txRet-------------------")
        #print(txRet)
        #print("------------------txRet-------------------")
        if (not txRet) or (0 == len(txRet)) : continue

        for iTry in range(10):
            if PushTxDataIntoDB(n, txRet):
                #print("push into db ok.")
                break 

    #txRet = GetTxDataFromDB(nStart, nStart+1)
    #if not txRet:
    #    print("GetTxDataInfoDB return empty.")
    #    return
    #print("-----------------")
    #print(txRet)

    pass



def main():
    while True:
        ScanBlock()
        time.sleep(15)
        break
    pass


def mainAddr():
    addrs =  GetExchangeUserAddress()
    print(addrs)

    pass





def main1():

    rpc =  EthProxy("192.168.10.199", 18545)
    result  = rpc.eth_getBlockByNumber(4263637)

    print(int(result["number"], 16))
    print(result["hash"])
    #print(int(result["size"], 16))
    print(len(result["transactions"]))


    for item in result["transactions"]:
        print("---------")
        
        jsonStr = json.dumps(item)
        strSql = """insert into json_test(person_desc) VALUES('{0}')""".format(jsonStr)
        #strSql = """insert into json_test(person_desc) VALUES('[{"name":"yqq", "id":999, "amout":9.999999999934}]');"""
        print(strSql)
        #print("strSql:" + strSql)
        sqlRet = sql.run(strSql)
        #print(type(jsonStr))
        #print(jsonStr)
        print(sqlRet)
        print("---------")

    pass


def main2():

    maxRet = GetMaxBlockNumberFromDB()
    if isinstance(maxRet, int):
        print(maxRet)
    else:
        print("sql error")


def main3():

    nBegin = 20
    nEnd = 50
    txRet = GetTxDataInfoDB(nBegin, nEnd)
    print(txRet)


if __name__ == '__main__':
    main()




