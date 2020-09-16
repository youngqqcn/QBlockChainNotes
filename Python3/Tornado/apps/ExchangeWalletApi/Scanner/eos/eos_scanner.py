#!coding:utf8

#author:yqq
#date:2019/12/24 0024 14:09
#description:  eos scanner


#
#算法B:  只扫不可逆区块, 按一个周期查询账户的余额, 对比上一个周期的余额,
#       如果余额没有变化, 则直接更新已扫区块高度;  若余额有变化,
#       则扫描这个周期内的所有的区块获取充币交易, 然后再更新已扫区块高度.
#
# 可能存在的问题
#  - 如果一个周期内减少的金额(转出)和增加的金额(充币)一样, 导致总的金额没有变化, 那么就会漏掉一些充值交易.
#  - 如果周期过大, 一次需要扫描的区块过多, 因为网络原因或其他原因, (总是)在中途失败,
#     那么就会导致"卡死"在某个区块高度, 无法扫到最新区块, 造成充币不到账的问题.
#
# # 有余额变化, 且变化大于 0.0001
#    # 21超级节点, 每个节点产生12个块, 需要(三分之二的超级节点确认), 两轮DPoS 确认之后才为不可逆区块
#    # 336 = 21 * 12 * (2/3) * 2
#    # 0.5 * 336     #每个区块间隔 0.5s
#    # 169 = 0.5 * 336 + 1    #等待的时间
#    # time.sleep( 169 )
#    # time.sleep( 85 )   #等待一轮DPOS时间,
#    # 将一次性等待改为, 边扫边等待,
#    # float_wait_secs = 85.0 / (abs(n_header_block_num - n_scanned_block) + 1)
#


import sys

if sys.version_info < (3, 0):
    print("please use python3")
    raise Exception("please use  python3 !!")



sys.path.append('.')
sys.path.append('..')

import time
import sql
import json
from  eos.eos_proxy import EosProxy
from dateutil import parser

import decimal
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 30
from utils import RoundDown
from utils import timestamp_parse
from pprint import  pprint
import requests


from config import EOS_ENABLE_SPEEDUP_PLUGIN
from config import EOS_RPC_HOST

class EosScanner(object):

    def __init__(self, node_host : str):
        self.rpcnode = EosProxy(node_host=node_host)
        self.addrs = self._GetAddresses()

    def _GetAddresses(self) -> list:

        """
        获取地址
        :return:   [addr1, addr2]
        """
        try:
            sqlstr = """SELECT DISTINCT `address` FROM `tb_eos_deposit_addrs`;"""
            sql_result = sql.run(sqlstr)
            addrs = []
            for item in sql_result:
                if 'address' not in item: continue
                addrs.append(item['address'].strip())
            return addrs
        except  Exception as e:
            print(" _GetAddresses() error: ", e)
            return []


    #从区块中获取交易所的充币交易
    def _GetDepositTrxsFromBlock(self, block_number) -> tuple:
        print('_GetDepositTrxsFromBlock : {}'.format(block_number))

        blkdata = self.rpcnode.chain_get_block(block_number)

        # 返回交易
        ret_trxs = []

        ret_out_tx_amount = []  # 记录转出的金额


        #判断 交易所收地址是否在区块中(是否包含字符串)
        strblkdata = json.dumps(blkdata)
        flag_contained = False
        for ex_account in self.addrs:
            if ex_account in strblkdata:
                flag_contained = True
                break

        if not flag_contained:
            return [], []




        transactions = blkdata['transactions']
        for tx in transactions:

            trx = tx['trx']
            if not isinstance( trx, dict) : continue

            #安全策略: 检查 transaction.status 必须为  executed
            status = tx['status']
            if status != 'executed': continue

            transaction = trx['transaction']
            if not  isinstance(transaction, dict): continue

            actions = transaction['actions']
            if not isinstance(actions, list) : continue
            if len(actions) == 0 or len(actions) >= 2: continue  #不支持批量充币


            act = actions[0]

            #安全策略:  检查  transaction.actions.account 必须为  eosio.token
            if act['account'] != 'eosio.token': continue

            #安全策略:  检查  合约函数名是否是 transfer
            if act['name'] != 'transfer' : continue

            data = act['data']
            if not isinstance(data, dict) : continue
            if 'from' not in data: continue
            if 'to' not in data: continue
            if 'quantity' not in data: continue
            if 'memo' not in data : continue


            #如果是转出交易, 则记录转出的金额
            if act['data']['from'] in self.addrs:
                stramount = act['data']['quantity'].replace('EOS', '').strip()
                ret_out_tx_amount.append(stramount)
                print('found a out tx ,  amount={}'.format(stramount))

            # 安全策略:  检查  to 是否是交易所接收地址
            acc_to = act['data']['to']
            if acc_to not in self.addrs:
                continue

            stramount = act['data']['quantity']
            if ' EOS' not in stramount: continue    #如果后期增加了其他的代币, 则需要添加对应symbol
            symbol = 'EOS'
            stramount = stramount.replace('EOS', '').strip()


            acc_from = act['data']['from']
            memo = act['data']['memo'] if  len(str(act['data']['memo']).strip()) != 0   else '1'
            memo = memo if memo.isdigit() else '1'




            #hex_data 是EOS代币交易相关, 暂时不解析 'hex_data'字段
            #后期如果需要对接 EOS代币, 则需要解析此字段

            txid = trx['id']
            nblocknumber = block_number
            ntimestamp = timestamp_parse(blkdata['timestamp'])


            founded_tx = {
                'txid' : txid,
                'blocknumber': nblocknumber,
                'timestamp' : ntimestamp,
                'src_account' : acc_from,
                'dst_account' : acc_to + '_' + memo,    #要满足格式: 目的地址_标签
                'symbol' : symbol,
                'amount' : stramount,
                'memo' : memo,
                'confirmations' : 100
            }

            ret_trxs.append(founded_tx)

        return  ret_trxs , ret_out_tx_amount

    #获取最新的余额(包括可逆交易)
    # def _GetBalance(self, account_name : str, symbol : str = 'EOS' ) -> Decimal :
    #     retdata = self.rpcnode.chain_get_currency_balance('eosio.token', account_name, symbol)
    #     strbalance = retdata[0].replace('EOS', '').replace(' ', '')
    #     return Decimal(strbalance)


    #获取最新的余额(包括可逆交易) 和 最新区块高度
    def _GetCoreLiquidBalanceAndHeaderBlockNum(self, account_name : str) -> tuple :
        retdata = self.rpcnode.chain_get_account(account_name)

        if 'head_block_num' not in retdata:
            print(f'{retdata}')
            raise Exception(f'{retdata}')


        #TODO: 如果节点访问不了,  返回为 none

        #需要判断 core_liquid_balance 是否存在,  如果 EOS余额为 0, 返回的数据没有 core_liquid_balance 字段
        if 'core_liquid_balance' not in retdata:
            strbalance =  '0.0000 EOS'
        else:
            strbalance =  retdata[ 'core_liquid_balance' ]
        strbalance = strbalance.replace('EOS', '').replace(' ', '')
        n_header_block_num = retdata['head_block_num']
        print(f'head_block_num:{n_header_block_num}, balance:{strbalance}')
        return n_header_block_num, Decimal(strbalance)


    def _GetBalanceAndScannedBlockFromDB(self, account_name : str):
        accname = account_name.strip()
        sqlstr = """SELECT `account`,`balance`,`scanned_block` FROM `tb_eos_scan_records` WHERE `account`='{}'; """.format(accname)
        sqlret = sql.run(sqlstr)
        return   sqlret[0]['account'],  sqlret[0]['balance'], int(sqlret[0]['scanned_block'])


    def _UpdateBalanceAndScannedBlockIntoDB(self, straccount_name : str, n_scanned_block_num : int, strbalance : str):
        accname = straccount_name.strip()
        balance = strbalance.strip()
        sqlstr = """UPDATE `tb_eos_scan_records` SET `balance`='{}', `scanned_block`={} WHERE `account`='{}';"""\
                    .format(balance, n_scanned_block_num, accname)
        print("sql: {}".format(sqlstr))
        sql.run(sqlstr)


    def _GetLatestIrreversibleBlockNumHeadBlockNum(self) -> tuple :
        retinfo = self.rpcnode.chain_get_info()
        n_irr_block_num = retinfo['last_irreversible_block_num']
        n_header_block_num = retinfo['head_block_num']
        return n_irr_block_num, n_header_block_num


    # https://open-api.eos.blockdog.com/
    # get_account_transfer
    def _SpeedUpPlugin_GetDepositTrxBlockNum(self, account_name : str, start_block_num : int, end_block_num : int) -> list:

        headers = {
            'content-type' : "application/json",
            'accept': 'application/json;charset=UTF-8',
            'apikey': '5b4added-e80c-41fb-b5a9-16269d2de79b'
        }
        page_size = 100
        str_url = 'https://open-api.eos.blockdog.com/v2/third/get_account_transfer'

        params = {
            "account_name": account_name,
            "code":"eosio.token",
            "symbol":"EOS",
            "type":1,                           #1 转入,  2 转出 ,  3 全部
            "start_block_num":start_block_num,  #起始区块高度
            "end_block_num": end_block_num,     #结束区块高度
            "sort":2,                           #2 升序   1 降序
            "size": page_size,
            "page":1
        }


        ret_blknums = []
        try:
            rspdata  = requests.post(url=str_url, data= json.dumps(params) , headers=headers)
            if rspdata.status_code != 200: raise  Exception( rspdata.text )
            rspdatajson = rspdata.json()
            if not isinstance( rspdatajson , dict):
                return []

            total = rspdatajson['total']
            page_count = int(total / page_size) + 1
            deposit_trxs = rspdatajson['list']

            #如果有分页, 处理分页
            if page_count >= 2:
                for page in range(2, page_count):
                    params['page'] = page
                    rsptmp = requests.post(url=str_url, data= json.dumps(params) , headers=headers)

                    if rsptmp.status_code != 200: raise  Exception(rsptmp.text)

                    rsptmpjson = rsptmp.json()
                    if not isinstance( rsptmpjson , dict): return []
                    deposit_trxs.extend( rsptmpjson['list'] )

            for trx in deposit_trxs:
                block_num = trx['block_num']
                if  start_block_num <= block_num < end_block_num:
                    ret_blknums.append(block_num)

        except Exception as e:
            print(e)

        return ret_blknums






    def StartScan(self, enable_speedup_plugin ):
        """
        开始扫描区块获取充币交易
        :param enable_speedup_plugin: 是否启用加速插件
        :return:
        """
        # print(' enable_speedup_plugin : {} '.format(enable_speedup_plugin))

        flag_need_sleep = False

        for each_account in self.addrs:

            #从数据库中获取 "已扫区块高度"  和  "余额"(在已扫区块高度处的余额)
            str_account, str_old_balance, n_scanned_block  =  self._GetBalanceAndScannedBlockFromDB(each_account)

            #获取链上  "最新不可逆区块高度"  和   "最新区块高度"  和 "最新余额"
            n_header_block_num, decm_latest_balance = self._GetCoreLiquidBalanceAndHeaderBlockNum(each_account)

            n_header_block_num += 1   #增加1 余额更新快过区块高度的更新

            decm_diff_value = decm_latest_balance - Decimal(str_old_balance)
            print('diff value: {}'.format(decm_diff_value))


            #因实际环境下, 每次请求需要将近 1s , 所以为了加快扫描速度, 不进行等待
            scan_block_range = range(n_scanned_block, n_header_block_num + 1)
            if  not enable_speedup_plugin:

                #考虑到 如果中间即有充币, 也有转出,  当充币的金额小于转出的金额时,
                # 余额变化量是负数, 如果直接跳过的话, 就会导致漏扫用户充币  所以  还是继续扫  2020-01-08 yqq
                #
                # 如果是余额 负增长 (从收币地址转出)
                # if decm_diff_value <= Decimal('0'):
                #     self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_header_block_num,
                #                                              '%.4f' % decm_latest_balance)
                #     continue

                # 如果余额  正增长 (有充币), 但是变化额度 小于 0.001 , 防止那些打广告的交易
                if Decimal('-0.001') <= decm_diff_value <= Decimal('0.001'):
                    # 更新数据库中的  "已扫区块高度" 和  "余额"
                    # self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_header_block_num, str_old_balance)
                    self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_header_block_num, '%.4f' % decm_latest_balance)
                    continue

                print('starting scan {} blocks, {} to {}.  '.format(len(scan_block_range), scan_block_range[0], scan_block_range[-1] ))
            else:
                # 调用第三方的接口, 获取包含充币交易的 区块的区块高度,
                # 为了交易所安全, 不直接使用第三方返回的交易信息, 仅获取区块高度,
                # 然后再到超节点提供的公共api查询区块内容, 获取充币交易信息
                scan_block_range = self._SpeedUpPlugin_GetDepositTrxBlockNum(each_account, n_scanned_block, n_header_block_num + 1)
                print('starting scan blocks {} .  '.format( scan_block_range ))
                pass


            # for n_cur_scan_blknum in range(n_scanned_block, n_header_block_num + 1):

            decm_tmp_new_balance = Decimal(str_old_balance)
            flag_scan_overed_in_advance = False  #当  老的余额 + 余额变化量 = 最新余额时 则 本次扫描提前结束
            for n_cur_scan_blknum in scan_block_range:

                if n_cur_scan_blknum == scan_block_range[-1]:
                    time.sleep(0.5)   #如果是最后一个块, 休眠0.5 , 为了防止扫描过快, 导致 n_header_block_num += 1 超过最新区块高度

                # print('sleep {} seconds'.format(float_wait_secs))
                # time.sleep(float_wait_secs)

                deposit_trxs , out_tx_amount = self._GetDepositTrxsFromBlock(n_cur_scan_blknum)

                # if (n_cur_scan_blknum - n_scanned_block) % 1 == 0:
                #     self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_cur_scan_blknum, str_old_balance)

                if len(deposit_trxs) == 0:
                    if len(out_tx_amount) == 0:
                        #每扫n个块更新一下数据库中中的  "已扫区块高度", 区块太多, 中途因为网络等原因, 出现"卡死"的问题
                        self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_cur_scan_blknum, str_old_balance)
                        print('not found any transaction in block {}'.format(n_cur_scan_blknum))
                        continue

                    for str_tmp_amount in out_tx_amount:
                        decm_tmp_new_balance += Decimal('-{}'.format(str_tmp_amount))
                        self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_cur_scan_blknum, '%.4f' % decm_tmp_new_balance)

                    # 老的余额 + 变化量  ≈ 最新余额
                    # 可以结束本次扫描了, 后面的不扫了
                    if Decimal('-0.001') < decm_latest_balance - decm_tmp_new_balance   < Decimal('0.001'):
                        # flag_scan_overed_in_advance = True
                        print('update out tx amount, tmp_balance equal latest_balance , scan overd in advance.')
                        break

                for trx in deposit_trxs:
                    sqlstr = """INSERT INTO tb_eos_deposit(`txid`, `timestamp`, `src_account`, `dst_account`, `block_number`, `symbol`, `amount`, `memo`, `confirmations`)"""
                    sqlstr += """VALUES('{}',{},'{}','{}',{},'{}','{}','{}', {})"""
                    sqlstr = sqlstr.format(trx['txid'], trx['timestamp'], trx['src_account'], trx['dst_account'],
                                           trx['blocknumber'], trx['symbol'], trx['amount'], trx['memo'], trx['confirmations'])
                    sqlstr += """ ON DUPLICATE KEY UPDATE `confirmations`={}; """.format(trx['confirmations'])
                    print("sql: {}  ".format(sqlstr))
                    sqlRet = sql.run(sqlstr)

                    #及时将余额变化量更新到数据库, 防止中途出现异常退出
                    decm_tmp_new_balance += Decimal(trx['amount'])
                    self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_cur_scan_blknum, '%.4f' % decm_tmp_new_balance)

                    # 老的余额 + 变化量  ≈ 最新余额
                    # 可以结束本次扫描了, 后面的不扫了
                    if  Decimal('-0.001') < decm_tmp_new_balance - decm_latest_balance  < Decimal('0.001'):
                        flag_scan_overed_in_advance = True
                        break


                #可以提前结束本次扫描了
                if flag_scan_overed_in_advance:
                    print('update deposit tx amount, tmp_balance equal latest_balance , scan overd in advance.')
                    break


            if enable_speedup_plugin: flag_need_sleep = True

            # 更新数据库中的  "已扫区块高度" 和  "余额"
            self._UpdateBalanceAndScannedBlockIntoDB(each_account, n_header_block_num, '%.4f' % decm_latest_balance)

        #休眠 尽可能将一次扫描的最多区块控制在500个区块以下
        #由不等式: sleep_secs * 2 + 85 * 2 < 500,  其中 85是检测到余额变化的情况下 额外等待的时间
        #  sleep_secs < 165
        # if flag_need_sleep:
        #     time.sleep(180)
        # if flag_need_sleep:
            # for i in range(5):
            #     strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            #     print("{} sleeping...".format(strtime))
            #     time.sleep(1)
            # time.sleep(10)

        pass



def main():

    strtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('-------{}-----------'.format(strtime))
    print('rpc host: {}'.format(EOS_RPC_HOST))
    # print('enable_speedup_plugin: {}'.format(EOS_ENABLE_SPEEDUP_PLUGIN))
    print('---------------------------')



    scanner = EosScanner(node_host=EOS_RPC_HOST)
    while True:
        try:
            scanner.StartScan( enable_speedup_plugin= False)
            time.sleep(1)
        except Exception as e:
            print("error: %s" % str(e))
            time.sleep(1)

    pass


if __name__ == '__main__':

    main()