#!coding:utf8

#author:yqq
#date:2020/7/9 0009 16:14
#description:


import json
from math import ceil
from pprint import pprint
from typing import List, Union

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response
MAX_RETRIES = 3

TIMEOUT_SECS = 20
from decimal import getcontext
getcontext().prec = 30


class JsonRpcError(IOError):#Exception):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        super(JsonRpcError, self).__init__(*args, **kwargs)

class BadConnectionError(JsonRpcError):
    pass

class BadStatusCodeError(JsonRpcError):
    pass

class BadJsonError(JsonRpcError):
    pass

class BadResponseError(JsonRpcError):
    pass



class BTCProxy(object):

    def __init__(self, host='localhost', port=3000, tls=False):
        self.host = host
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=MAX_RETRIES))

    def _post_json_call(self, endpoint, params):

        data = params
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}/{}'.format(scheme, self.host, self.port, endpoint)
        # print("url:" + url)
        headers = {'Content-Type': "application/json"}
        Response()
        try:
            r = self.session.post(url, headers=headers, data=json.dumps(data), timeout=TIMEOUT_SECS)
        except RequestsConnectionError:
            raise BadConnectionError("connect bitcoin api server failed.")
        except Exception as e:
            errMsg = "error:{}".format(e)
            raise BadConnectionError("%s" % errMsg)

        if r.status_code != 200:
            raise BadStatusCodeError("HTTP%d:%s" % (r.status_code, r.text))
        try:
            return r.text
        except Exception as e:
            raise BadJsonError("error:{}, error:{}".format(str(r.text), e))

    def _post_text_call(self, endpoint , params):

        data = params
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}/{}'.format(scheme, self.host, self.port, endpoint)
        # print("url:" + url)
        headers = {'Content-Type': "text/plain"}
        Response()
        try:
            r = self.session.post(url, headers=headers, data=data, timeout=TIMEOUT_SECS)
        except RequestsConnectionError:
            raise BadConnectionError("connect bitcoin api server failed.")
        except Exception as e:
            errMsg = "error:{}".format(e)
            raise BadConnectionError("%s" % errMsg)

        if r.status_code != 200:
            raise BadStatusCodeError("HTTP%d:%s" % (r.status_code, r.text))
        try:
            return r.text
        except Exception as e:
            raise BadJsonError("error:{}, error:{}".format(str(r.text), e))


    def _get_url_call(self, endpoint: str):
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}/{}'.format(scheme, self.host, self.port, endpoint)
        # print("url:" + url)
        Response()
        try:
            r = self.session.get(url, timeout=TIMEOUT_SECS)
        except RequestsConnectionError:
            raise BadConnectionError("connect bitcoin api server failed.")


        if r.status_code != 200:
            raise BadStatusCodeError(r.status_code)
        try:
            return r.text
        except Exception as e:
            raise BadResponseError("bad response.error:{}".format(e))
        pass




    def get_balance(self, address: str, mem_spent: bool =True, mem_recv: bool =False) -> int :
        """
        获取地址余额, 返回 以 satoshi 为单位
        :param address:
        :param mem_spent: 是否将未确认的发送交易(转出), 计算在内
        :param mem_recv: 是否将未确认的接收(转入), 计算在内
        :return:
        {
            "address": "mjGRnCSyan333FdQVKonTFTmNqESaHUJmt",
            "chain_stats": {
                "funded_txo_count": 117,
                "funded_txo_sum": 584900001000,
                "spent_txo_count": 3,
                "spent_txo_sum": 15000000000,
                "tx_count": 118
            },
            "mempool_stats": {
                "funded_txo_count": 0,
                "funded_txo_sum": 0,
                "spent_txo_count": 0,
                "spent_txo_sum": 0,
                "tx_count": 0
            }
        }
        """
        endpoint = f'address/{address}'
        ret = self._get_url_call(endpoint=endpoint)
        addr_info = json.loads(ret)

        chain_stats = addr_info['chain_stats']
        sum = chain_stats['funded_txo_sum'] - chain_stats['spent_txo_sum']
        mempool_stats = addr_info['mempool_stats']
        if mem_recv:
            sum += mempool_stats['funded_txo_sum']
        if mem_spent:
            sum -=  mempool_stats['spent_txo_sum']

        return sum


    def get_utxo(self, address: str, include_mem: bool = True ) -> List[ Union[dict, None]]:
        """
        获取地址的 utxo ,  , 返回字典数组, 最多返回500个utxo
        :param address:
        :param include_mem: 是否包含未确认的 utxo?
        :return:
        """
        endpoint = f'address/{address}/utxo'
        ret = self._get_url_call(endpoint=endpoint)
        utxos = json.loads(ret)

        result = []
        if include_mem:
            result = utxos
        else:
            for utxo in utxos:
                if utxo['status']['confirmed'] == True:
                    result.append(utxo)
        return result

    def get_block_info(self, block_hash: str) -> dict:
        """
        获取区块信息(区块头)
        :param block_hash:
        :return:
        """

        endpoint = f'block/{block_hash}'
        ret = self._get_url_call(endpoint=endpoint)
        blk_info = json.loads(ret)
        return blk_info



    def get_block_txs(self, block_hash: str, start_index: int) -> List[ Union[dict, None]]:
        """
        获取区块的交易
        :param block_hash:
        :param start_index: 起始索引, 必须是25的倍数(0, 25, 50)
        :return: [{}, {}]
        """

        # blk_info = self.get_block_info(block_hash=block_hash)
        # tx_count = blk_info['tx_count']
        #
        # total_pages = ceil(tx_count / 25)
        #
        # for page_idx in range(total_pages):
        #     start_index = page_idx * 25
        #     endpoint = f'block/{block_hash}'

        endpoint = f'block/{block_hash}/txs/{start_index}'
        ret = self._get_url_call(endpoint=endpoint)
        txs = json.loads(ret)
        return txs


    def get_block_hash(self, block_height: int) -> str:
        """
        根据区块高度获取区块hash
        :param block_height:
        :return:
        """
        endpoint = f'block-height/{block_height}'
        ret = self._get_url_call(endpoint=endpoint)
        block_hash = str(ret)
        return block_hash


    def get_latest_height(self) -> int:
        """
        获取当前最新区块高度
        :return:
        """
        endpoint = f'blocks/tip/height'
        ret = self._get_url_call(endpoint=endpoint)
        block_height = int(ret)
        return block_height



    def is_orphan_block(self, block_hash: str) -> bool:
        """
        判断是否是孤儿区块
        :return:
        """
        endpoint = f'block/{block_hash}/status'
        ret = self._get_url_call(endpoint=endpoint)
        blk_status = json.loads(ret)
        return  not blk_status['in_best_chain']

    def get_transaction(self, txid: str) -> Union[dict, None]:
        """
        获取交易的信息
        :param txid:
        :return:
        """
        endpoint = f'tx/{txid}'
        ret = self._get_url_call(endpoint=endpoint)
        tx = json.loads(ret)
        return tx


    def get_address_txs(self, address: str) -> List[ Union[dict, None]]:
        """
        获取地址所有交易
        :param address:
        :return:
        """
        endpoint = f'address/{address}/txs'
        ret = self._get_url_call(endpoint=endpoint)
        txs = json.loads(ret)
        return txs


    def get_recommand_fee(self) -> int:
        """获取推荐的手续费"""
        endpoint = f'fee-estimates'
        ret = self._get_url_call(endpoint=endpoint)
        fee_dict = json.loads(ret)
        return fee_dict


    def send_raw_tx(self, raw_tx_hex: str) -> str:
        """
        广播交易
        :return: 如果广播成功返回  txid
        """
        endpoint = 'tx'
        txid = self._post_text_call(endpoint=endpoint, params=raw_tx_hex)
        txid  = str(txid)
        return txid





def main():

    host = '192.168.10.199'
    port = 3002
    proxy = BTCProxy(host=host, port=port)


    # balance = proxy.get_balance(address='moAt6v6gpfJhSBYSmS2AzanW9565kakujW')
    # print(balance)
    #
    # utxos = proxy.get_utxo(address='moAt6v6gpfJhSBYSmS2AzanW9565kakujW', include_mem=False)
    # print( json.dumps(utxos, indent=4) )
    #
    # blk_info = proxy.get_block_info(block_hash='4b002206a7420a96821d4562ae5435c2ec8e77bea07bec0ab452143bc78ec5bd')
    # print(json.dumps( blk_info, indent=4))

    # txs = proxy.get_block_txs(block_hash='4b002206a7420a96821d4562ae5435c2ec8e77bea07bec0ab452143bc78ec5bd', start_index=0)
    # print(json.dumps( txs, indent=4))

    #
    # blk_hash = proxy.get_block_hash(block_height=154)
    # print(blk_hash)
    #
    # height =  proxy.get_latest_height()
    # print(height)
    #
    # is_orphan = proxy.is_orphan_block(block_hash='4b002206a7420a96821d4562ae5435c2ec8e77bea07bec0ab452143bc78ec5bd')
    # print(is_orphan)


    tx_data = '0100000001931d92d85ff9e291026f3361a8b206917ecd52aaf528ac6ee826ce3e94acc75d000000006a473044022066aae91621a9320d9025f36b6ff83b087aea80828cd06c5e7fc10fb9bee0d29f02207417b7b29aebf148eb87138d6f4428468c93f97220d403a2a8384387472727870121029ea9445d4651e9927c438d64eced89db41d524ffcfa07519c061cd2b077ee658ffffffff0118ddf5050000000016001486359e19ae88dfd575f933fd91f853891a70075700000000'
    txid = proxy.send_raw_tx(raw_tx_hex=tx_data)
    print(txid)

    pass


if __name__ == '__main__':

    main()