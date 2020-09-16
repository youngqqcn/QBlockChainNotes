#-*- coding:utf-8 -*-
# 定时


import decimal
import os
from decimal import Decimal

from lib.cosmos_proxy import CosmosProxy

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PG_Admin.settings")
import sys
sys.path.append('/data/PaymentGateway')
sys.path.append('/data/PaymentGateway/PG_Admin')
sys.path.insert(0, '/data/PaymentGateway')
sys.path.insert(0, '/data/PaymentGateway')
# 导入Django
import django
# 运行Django项目
django.setup()
import time
import pymysql
from datetime import datetime
import requests
from PG_Admin.settings import ETH_FULL_NODE_HOST, ETH_FULL_NODE_PORT, EIP20_ABI, ERC20_USDT_CONTRACT_ADDRESS, ENV_NAME, \
    HTDF_NODE_RPC_HOST, HTDF_NODE_RPC_PORT, BTC_API_HOST, BTC_API_PORT, g_IS_MAINNET, REDIS_HOST, REDIS_PORT, \
    REDIS_API_KEY_DB_NAME_CACHE
from config.config import config
from eth_typing import HexStr, URI
from eth_utils import to_checksum_address
from web3 import Web3, HTTPProvider
from pgadmin.models import UserTokenBalances, Project
from lib.btc_proxy import BTCProxy
import redis

if g_IS_MAINNET:
    HTDF_CHAINID = 'mainchain'
    HRC20_CONTRACT_MAP = {
        # 例如: "contract_addr" : { "decimal": 精度, "symbol":"AJC"  }
        "htdf1w43aazq9sjlcrwj4y7nnsck7na5zljzu4x5nrq": {"decimal": 18, "symbol": "BTU"},
    }
else:
    HTDF_CHAINID = 'testchain'

    HRC20_CONTRACT_MAP = {
        # 例如: "contract_addr" : { "decimal": 精度, "symbol":"AJC"  }
        "htdf1vw4dq4teurls7yg8254pz5esn0gpg0492yvt95": {"decimal": 18, "symbol": "BTU"},
    }


address_token = ['HTDF', 'ETH', 'BTC']
all_token = ['HTDF', 'ETH', 'USDT', 'BTC', 'BTU']

db = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PWD,
                     port=config.MYSQL_PORT, database=f'pg_database_{ENV_NAME.lower()}',
                     autocommit=True, read_timeout=10, write_timeout=10)

cursor = db.cursor()

def round_down(decim):
    if isinstance(decim, Decimal):
        decimalFormat = decim.quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    # elif isinstance(decim, int):
    else:
        decimalFormat = Decimal(str(decim)).quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    return decimalFormat


#初始化谷歌验证码

def init_google_key_in_redis():
    rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE, decode_responses=True)

    is_exist = rds.get(f'{ENV_NAME}_exist_google_key')
    if is_exist:
        pass
    else:
        sql = "select * from tb_google_code"
        cursor.execute(sql)
        data = cursor.fetchall()
        for i in data:
            pro_id = str(i[1])
            secret = i[2]
            logined = i[3]
            is_superuser = i[4]

            if is_superuser == 1:
                url = f'{ENV_NAME}_code_admin_' + pro_id
                rds.set(url, secret)
            else:
                url = f'{ENV_NAME}_code_' + pro_id
                rds.set(url, secret)

            if logined == 1:
                url = f'{ENV_NAME}_first_login_' + pro_id
                rds.set(url, str(datetime.now()))

        url = f'{ENV_NAME}_exist_google_key'
        rds.set(url, str(datetime.now()))


    pass




def select_address_admin_action():
    #查询地址管理  Address
    try:
        print(f'into signal user: admin , model: user_address , action: select')

        sql = "select pro_id from tb_project"
        cursor.execute(sql)
        select_user = cursor.fetchall()

        sql = "select DISTINCT pro_id from tb_address_admin"
        cursor.execute(sql)
        data = cursor.fetchall()

        sql = "select DISTINCT pro_id, token_name from tb_address"
        cursor.execute(sql)
        order_data = cursor.fetchall()

        print(f'user_address : 地址管理创建中!')

        for i in select_user:
            count = 0
            len_address_token = 0
            list_token = []
            creat_data = []
            pro_id = i[0]

            for p in order_data:
                if p[0] == pro_id:
                    len_address_token += 1
                    list_token.append(p[1])

            for k in data:
                if pro_id == k[0]:
                    count += 1

            print(f'pro_id: {pro_id} 地址管理币种数量 count: {count}, 子地址币种数量 len_address_token: {len_address_token}')

            if count == len_address_token:
                print(f'user_address : pro_id:{pro_id} 没有缺币种 正常跳过!')
                continue
            else:
                # 删除所有关于这个id的币种,重建
                if count != 0:
                    sql = "delete from tb_address_admin where pro_id=%d"%(pro_id)
                    cursor.execute(sql)
                    db.commit()
                    print(f'user_address : pro_id:{pro_id} 删除所有币种')

                for p in list_token:
                    creat_data.append((p, 0, 0, i[0], str(datetime.now())))

                for j in creat_data:
                    sql = """insert into tb_address_admin (token_name, address_nums, uncharged_address_nums, pro_id, 
                    update_time) value('%s', %d, %d, %d, '%s') """%(j[0], j[1], j[2], j[3], j[4])
                    cursor.execute(sql)
                db.commit()
                print(f'user_address : pro_id:{pro_id} 重建地址管理数据!')

        list_data = []

        print(f'user_address : 地址管理创建完毕!')
        print(f'user_address : 地址管理更新中!')

        for j in select_user:

            for i in address_token:
                sql = """select tb_address.addr_nums, tb_address.addr_nums-tb_active_address_balances.active_nums, 
                tb_address_admin.id, tb_address.pro_id, tb_address.token_name from (select count(address) 
                as addr_nums, token_name, pro_id from tb_address where token_name='%s' and pro_id=%d) as tb_address, 
                (select count(address) as active_nums from tb_active_address_balances 
                where token_name='%s' and pro_id=%d) 
                as tb_active_address_balances , tb_address_admin where IFNULL(tb_address.pro_id, '') and
                tb_address_admin.pro_id = tb_address.pro_id and tb_address_admin.token_name = tb_address.token_name
                """%(i, j[0], i, j[0])
                cursor.execute(sql)
                data = cursor.fetchall()
                if len(data) != 0:
                    update_data = (data[0][0], data[0][1], str(datetime.now()), data[0][2], data[0][3], data[0][4])
                    list_data.append(update_data)
                print(f'update pro_id : {j[0]}')
        sql = "update tb_address_admin set address_nums=%s, uncharged_address_nums=%s, update_time=%s where id=%s " \
              "and pro_id=%s and token_name=%s;"
        cursor.executemany(sql, list_data)
        db.commit()
        print(f'user_address : 地址管理更新完毕!')
        print(f'address write mysql {len(list_data)}')
    except Exception as e:
        print(f'select_address_admin_action error: {e} ')
        pass


def select_withdraw_address_balance():

    #查询提币地址余额
    print(f'into signal user: admin , model: withdraw_address_balance_user , action: select')

    sql = "select pro_id from tb_project"
    cursor.execute(sql)
    select_user = cursor.fetchall()

    for k in select_user:
        k = k[0]
        user = Project.objects.get(pro_id=k)

        sql = "select token_name, address  from tb_withdraw_config where pro_id=%d"%(k)
        cursor.execute(sql)
        select_withdrawconfig = cursor.fetchall()

        for j in select_withdrawconfig:
            try:
                if j[0] == "HTDF":
                    # host = 'htdf2020-test01.orientwalt.cn'
                    # port = 1317

                    from_addr = j[1]

                    HTDF_RPC_HOST = f'{HTDF_NODE_RPC_HOST}:{HTDF_NODE_RPC_PORT}'
                    url = 'http://%s/bank/balances/%s' % (HTDF_RPC_HOST.strip(), from_addr.strip())
                    print(f'url:{url}')
                    rsp = requests.get(url=url, timeout=10)

                    amount = 0

                    if rsp.status_code != 200:
                        print(f'get account info error: {rsp.status_code}')

                    else:
                        retList = rsp.json()
                        for item in retList:
                            if item["denom"] == "usdp" or item["denom"] == "htdf" or item["denom"] == "het":
                                amount = str(item["amount"])

                    # if amount == '0':
                    #     print(f'{j.token_name} amount: {amount} -- if amount = 0 continue')
                    #     continue

                    update_UserTokenBalances = UserTokenBalances.objects.filter(pro_id=k,
                                    token_name=j[0], withdraw_address=from_addr).first()
                    if update_UserTokenBalances:
                        update_UserTokenBalances.withdraw_balance = amount
                        update_UserTokenBalances.update_time = datetime.now()
                        update_UserTokenBalances.save()
                        print(f'token_name : HTDF address : {from_addr} action: update success')
                    else:
                        UserTokenBalances.objects.create(pro_id=user,token_name=j[0], all_balance=0,
                        withdraw_address=from_addr, withdraw_balance=amount, update_time=datetime.now())
                        print(f'token_name : HTDF address : {from_addr} action: creat success')


                elif j[0] == "BTC":

                    from_addr = j[1]
                    print(f'token_name : BTC address : {from_addr}')
                    proxy = BTCProxy(host=BTC_API_HOST, port=BTC_API_PORT)
                    balance_in_satoshi = proxy.get_balance(address=from_addr, mem_spent=True, mem_recv=True)
                    balance_in_btc = round_down(Decimal(balance_in_satoshi) / Decimal(10 ** 8))

                    update_UserTokenBalances = UserTokenBalances.objects.filter(pro_id=k, token_name=j[0],
                                                        withdraw_address=from_addr).first()
                    if update_UserTokenBalances:
                        update_UserTokenBalances.withdraw_balance = balance_in_btc
                        update_UserTokenBalances.update_time = datetime.now()
                        update_UserTokenBalances.save()
                        print(f'token_name : BTC address : {from_addr} action: update success')
                    else:
                        UserTokenBalances.objects.create(pro_id=user, token_name=j[0], all_balance=0,
                                                         withdraw_address=from_addr, withdraw_balance=balance_in_btc,
                                                         update_time=datetime.now())
                        print(f'token_name : BTC address : {from_addr} action: creat success')

                    pass

                elif j[0] == "ETH":
                    # host = '192.168.10.199'
                    # port = 28545

                    from_addr = j[1]

                    ETH_FULL_NODE_RPC_URL = 'http://{}:{}'.format(ETH_FULL_NODE_HOST, ETH_FULL_NODE_PORT)
                    print(f'url : {ETH_FULL_NODE_RPC_URL}')
                    block_identifier = HexStr('latest')  # 不能用pending
                    myweb3 = Web3(provider=HTTPProvider(endpoint_uri=URI(ETH_FULL_NODE_RPC_URL)))
                    nbalance = myweb3.eth.getBalance(account=to_checksum_address(from_addr),
                                                     block_identifier=block_identifier)
                    ether_balance = str(myweb3.fromWei(nbalance, 'ether'))  # ETH 余额

                    # decim_eth_balance = round_down(ether_balance)
                    # if ether_balance == '0':
                    #     print(f'{j.token_name} amount: {ether_balance} -- if amount = 0 continue')
                    #     continue
                    update_UserTokenBalances = UserTokenBalances.objects.filter(pro_id=k,
                                    token_name=j[0], withdraw_address=from_addr).first()
                    if update_UserTokenBalances:
                        update_UserTokenBalances.withdraw_balance = ether_balance
                        update_UserTokenBalances.update_time = datetime.now()
                        update_UserTokenBalances.save()
                        print(f'token_name : ETH address : {from_addr} action: update success')

                    else:
                        UserTokenBalances.objects.create(pro_id=user,token_name=j[0], all_balance=0,
                        withdraw_address=from_addr, withdraw_balance=ether_balance, update_time=datetime.now())
                        print(f'token_name : ETH address : {from_addr} action: creat success')

                    pass

                elif j[0] == "USDT":

                    chksum_contract_addr = to_checksum_address(ERC20_USDT_CONTRACT_ADDRESS)
                    from_addr = j[1]

                    ETH_FULL_NODE_RPC_URL = 'http://{}:{}'.format(ETH_FULL_NODE_HOST, ETH_FULL_NODE_PORT)
                    print(f'url : {ETH_FULL_NODE_RPC_URL}')
                    myweb3 = Web3(provider=HTTPProvider(endpoint_uri=URI(ETH_FULL_NODE_RPC_URL)))
                    contract = myweb3.eth.contract(address=chksum_contract_addr, abi=EIP20_ABI)
                    erc20_token_balance_int = contract.functions.balanceOf(to_checksum_address(from_addr)).call()

                    # if erc20_token_balance_int == 0:
                    #     print(f'{j.token_name} amount: {erc20_token_balance_int} -- if amount = 0 continue')
                    #     continue

                    erc20_token_balance_decimal = str(myweb3.fromWei(erc20_token_balance_int, unit='mwei'))

                    # if erc20_token_balance_decimal == '0':
                    #     print(f'{j.token_name} amount: {erc20_token_balance_decimal} -- if amount = 0 continue')
                    #     continue

                    update_UserTokenBalances = UserTokenBalances.objects.filter(pro_id=k,
                                                                                token_name=j[0],
                                                                                withdraw_address=from_addr).first()
                    if update_UserTokenBalances:
                        update_UserTokenBalances.withdraw_balance = erc20_token_balance_decimal
                        update_UserTokenBalances.update_time = datetime.now()
                        update_UserTokenBalances.save()
                        print(f'token_name : USDT address : {from_addr} action: update success')

                    else:
                        UserTokenBalances.objects.create(pro_id=user, token_name=j[0], all_balance=0,
                                                         withdraw_address=from_addr, withdraw_balance=erc20_token_balance_decimal,
                                                         update_time=datetime.now())
                        print(f'token_name : USDT address : {from_addr} action: creat success')


                elif j[0] == "BTU":

                    from_addr = j[1]

                    hrc20_contract = ''
                    hrc20_decimals = 18
                    for con_addr, sym_info in HRC20_CONTRACT_MAP.items():
                        if sym_info['symbol'] == j[0]:
                            hrc20_contract = con_addr
                            hrc20_decimals = sym_info['decimal']

                    assert len(hrc20_contract) == 43, 'hrc20_contract is illegal'
                    assert hrc20_decimals == 18, 'hrc20_deciaml not equal 18'

                    rpc = CosmosProxy(host=HTDF_NODE_RPC_HOST, port=HTDF_NODE_RPC_PORT, cointype=j[0])

                    strbalance = rpc.getHRC20TokenBalance(contract_addr=hrc20_contract, address=from_addr)
                    token_balance = round_down(Decimal(strbalance))

                    update_UserTokenBalances = UserTokenBalances.objects.filter(pro_id=k,
                                                                                token_name=j[0],
                                                                                withdraw_address=from_addr).first()
                    if update_UserTokenBalances:
                        update_UserTokenBalances.withdraw_balance = token_balance
                        update_UserTokenBalances.update_time = datetime.now()
                        update_UserTokenBalances.save()
                        print(f'token_name : BTU address : {from_addr} action: update success')

                    else:
                        UserTokenBalances.objects.create(pro_id=user, token_name=j[0], all_balance=0,
                                                         withdraw_address=from_addr, withdraw_balance=token_balance,
                                                         update_time=datetime.now())
                        print(f'token_name : BTU address : {from_addr} action: creat success')


            except Exception as e:
                print(f'select withdraw_address_balance error: {e}')


def select_AssetDailyReport():
    try:
        #日报表查询
        print(f'into AssetDailyReport user: admin , model: AssetDailyReport_user , action: select')

        list_data = []
        sql = "select pro_id from tb_project"
        cursor.execute(sql)
        select_user = cursor.fetchall()

        sql = "select pro_id from tb_asset_daily_report where to_days(update_time)=to_days(now())"
        cursor.execute(sql)
        data = cursor.fetchall()

        sql = "select DISTINCT pro_id, token_name from tb_withdraw_config"
        cursor.execute(sql)
        token_data = cursor.fetchall()

        print('AssetDailyReport  创建中!')

        for i in select_user:
            count = 0
            len_address_token = 0
            list_token = []
            creat_data = []

            for p in token_data:
                if p[0] == i[0]:
                    len_address_token += 1
                    list_token.append(p[1])

            for k in data:
                if i[0] == k[0]:
                    count += 1

            if count == len_address_token:
                print(f'AssetDailyReport : pro_id:{i[0]} 没有缺币种 正常跳过!')

                continue
            else:
                # 删除所有关于这个id的币种,重建
                if count != 0:
                    sql = "delete from tb_asset_daily_report where pro_id=%d and to_days(update_time)=to_days(now())" % (i[0])
                    cursor.execute(sql)
                    db.commit()
                    print(f'AssetDailyReport pro_id : {i[0]} 删除当天所有日报表资产信息')

                for p in list_token:
                    creat_data.append((p, 0, 0, 0, 0, str(datetime.now()), i[0]))
                    print(f'pro_id: {i[0]}-->token_name: {p}')

                for j in creat_data:
                    sql = """insert into tb_asset_daily_report (token_name, deposit_amount, withdraw_amount, 
                    collectionRecords_amount, all_balance, update_time, pro_id) 
                        value('%s', %d, %d, %d, %d, '%s', %d) """ % (j[0], j[1], j[2], j[3], j[4], j[5], j[6])
                    cursor.execute(sql)
                db.commit()
                print(f'AssetDailyReport pro_id : {i[0]} 创建当天所有日报表资产信息')

        print('AssetDailyReport  创建完毕!')
        print('AssetDailyReport  更新中!')

        for k in select_user:
            k = k[0]

            for i in all_token:
                sql = """select report.id, active.token_name, IFNULL(active.active_balances, 0.00000000), 
                IFNULL(deposit.amount, 0.00000000), IFNULL(withdraw.amount, 0.00000000), IFNULL(collection.amount,
                 0.00000000) from (select sum(balance) as active_balances, token_name from tb_active_address_balances 
                 where pro_id=%d and token_name='%s') as active, (select sum(amount) as amount from tb_deposit where 
                 pro_id=%d and token_name='%s' and to_days(block_time)=to_days(now())) as deposit, (select sum(amount) as 
                 amount from tb_withdraw_order where pro_id=%d and token_name='%s' and to_days(block_time)=to_days(now()) 
                 and order_status='SUCCESS') as withdraw, (select sum(amount) as amount from tb_collection_records where 
                 pro_id=%d and token_name='%s' and to_days(block_time)=to_days(now()) and transaction_status='SUCCESS') 
                 as collection, (select id as id from tb_asset_daily_report where pro_id=%d and token_name='%s' and 
                 to_days(update_time)=to_days(now())) as report;
                """%(k, i, k, i, k, i, k, i, k, i)
                cursor.execute(sql)
                data = cursor.fetchall()
                if len(data) != 0:
                    update_data = (data[0][2], str(datetime.now()), data[0][3], data[0][4], data[0][5], data[0][0],
                                   data[0][1])
                    list_data.append(update_data)

            sql = """update tb_asset_daily_report set all_balance=%s, update_time=%s, deposit_amount=%s, withdraw_amount=%s,
             collectionRecords_amount=%s where id=%s and token_name=%s;"""
            cursor.executemany(sql, list_data)
        db.commit()
        print('AssetDailyReport  更新完毕!')

    except Exception as e:
        print(f'select_AssetDailyReport {e}')
        pass



def main():

    #初始化谷歌验证码
    print('初始化谷歌验证码到redis中 - - - - - - >')
    init_google_key_in_redis()
    print('初始化谷歌验证码完毕 - - - - - - - - - >')

    cap_time = 60*60 if str(ENV_NAME).upper() == 'PRO' else 5*60

    while True:
        try:
            print(f'查询地址管理报表 {datetime.now()}')
            select_address_admin_action()
            print(f'查询地址管理报表完成: {datetime.now()}')
        except Exception as e:
            print(f'查询地址管理报表出错: {e}')
            pass

        try:
            print(f'查询子地址余额报表: {datetime.now()}')
            select_withdraw_address_balance()
            print(f'查询子地址余额报表完成: {datetime.now()}')
        except Exception as e:
            print(f'查询子地址余额报表出错: {e}')
            pass

        try:
            print(f'查询日资产报表: {datetime.now()}')
            select_AssetDailyReport()
            print(f'查询日资产报表完成: {datetime.now()}')
        except Exception as e:
            print(f'查询日资产报表出错: {e}')
            pass

        for i in range(int(cap_time // 60)):
            print(f'休眠中....{datetime.now()}')
            time.sleep(60)

    pass


if __name__ == '__main__':

    main()
