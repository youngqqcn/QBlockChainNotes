#coding:utf8




def GetScanStartBlock(strCoinType):
    """
    从数据库中获取币种的 扫描的起始区块
    """

    #类型判断
    assert (isinstance( strCoinType, str) or isinstance(strCoinType, unicode))

    #对参数进行检查
    #注意sql注入
    strType = strCoinType.lower()
    if 'eth' == strType:
        pass
    elif 'usdp' == strType:
        pass
    elif 'htdf' == strType:
        pass
    else:
        return 0
        pass

    import sql
    sqlRet = sql.run("""select start_block from t_scan_start where coin_type='{0}'""".format(strType))
    if len(sqlRet) > 0 :
        item = sqlRet[0]
        if 'start_block' in item:
            nRet = int(str(item['start_block']), 10)
            return nRet
    return 0



def main():
    print(GetScanStartBlock('eth'))
    print(GetScanStartBlock('btc'))


    pass


if __name__ == '__main__':
    main()
