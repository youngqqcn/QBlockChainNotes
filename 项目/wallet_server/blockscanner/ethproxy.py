#coding:utf8
import json
import warnings

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response
import exceptions
#from exceptions import  BadJsonError, BadResponseError, BadStatusCodeError
#from exceptions import BadConnectionError


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


BLOCK_TAG_EARLIEST = 'earliest'
BLOCK_TAG_LATEST   = 'latest'
BLOCK_TAG_PENDING  = 'pending'
BLOCK_TAGS = (
    BLOCK_TAG_EARLIEST,
    BLOCK_TAG_LATEST,
    BLOCK_TAG_PENDING,
)

GETH_DEFAULT_RPC_PORT = 18545
MAX_RETRIES = 3
JSON_MEDIA_TYPE = 'application/json'

def validate_block(block):
    if isinstance(block, basestring):
        if block not in BLOCK_TAGS:
            raise ValueError('invalid block tag')
    if isinstance(block, int):
        block = hex(block)
    return block

class EthProxy(object):


    def __init__(self, host='localhost', port=GETH_DEFAULT_RPC_PORT, tls=False):
        self.host = host
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=MAX_RETRIES))

    #使用ethscan.io的api  备用方案: 2019-05-16  by yqq
    def _call_proxy(self, method, params=None, _id=1):

        params = params or []

        strParams = ""
        if method == 'eth_getBlockByNumber':
            if len(params) == 0: 
                raise BadJsonError("args error.")
            strParams = "api?module=proxy&action=eth_getBlockByNumber&tag={0}&boolean=true&apikey=CMBN61ZYD517UW359EVRFCNX1MN48W37N2".format(str(params[0])) #十六进制
            pass
        elif method == 'eth_blockNumber':
            strParams = "api?module=proxy&action=eth_blockNumber&apikey=CMBN61ZYD517UW359EVRFCNX1MN48W37N2"
            pass


        url = 'https://{}/{}'.format( self.host, strParams)
        print("url is :"+url)
        headers = {'Content-Type': JSON_MEDIA_TYPE}
        Response()
        try:
            #r = self.session.post(url, headers=headers, data=json.dumps(data))
            r = requests.get(url)
        except RequestsConnectionError:
            raise BadConnectionError("request ethereum node failed, please contact system administrator to check node server.") #fixed bug, 2019-04-13 yqq
        if r.status_code / 100 != 2:
            raise BadStatusCodeError(r.status_code)

        try:
            print("------1-------")
            response = r.json()
            #print(response)
            print("------1------")
        except ValueError:
            raise BadJsonError("json error:" + str(r.text))

        try:
            print("------2-------")
            print(response['result'])
            print("------2------")
            return response['result']
        except KeyError:
            raise BadResponseError(response)



    def _call(self, method, params=None, _id=1):
            

        #使用备用代理方案
        if "etherscan.io" in self.host:
            return self._call_proxy(method, params, _id)

        params = params or []

        data = {
            'jsonrpc': '2.0',
            'method':  method,
            'params':  params,
            'id':      _id,
        }
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}'.format(scheme, self.host, self.port)
        headers = {'Content-Type': JSON_MEDIA_TYPE}
        Response()
        try:
            r = self.session.post(url, headers=headers, data=json.dumps(data))
        except RequestsConnectionError:
            raise BadConnectionError("request ethereum node failed, please contact system administrator to check node server.") #fixed bug, 2019-04-13 yqq
        if r.status_code / 100 != 2:
            raise BadStatusCodeError(r.status_code)
        try:
            response = r.json()
        except ValueError:
            raise BadJsonError("json error:" + str(r.text))
        try:
            return response['result']
        except KeyError:
            raise BadResponseError(response)


    def eth_getBlockByHash(self, block_hash, tx_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbyhash

        TESTED
        '''
        return self._call('eth_getBlockByHash', [block_hash, tx_objects])

    def eth_getBlockByNumber(self, block=BLOCK_TAG_LATEST, tx_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbynumber

        TESTED
        '''
        #block = validate_block(block)
        blockNumber = block
        if '0x' not in str(block): blockNumber = hex(int(blockNumber))
        return self._call('eth_getBlockByNumber', [blockNumber, tx_objects])

    def eth_getTransactionByHash(self, tx_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyhash

        TESTED
        '''
        return self._call('eth_getTransactionByHash', [tx_hash])

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblockhashandindex

        TESTED
        '''
        return self._call('eth_getTransactionByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getTransactionByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblocknumberandindex

        TESTED
        '''
        block = validate_block(block)
        return self._call('eth_getTransactionByBlockNumberAndIndex', [block, hex(index)])

    def eth_blockNumber(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_blocknumber

        TESTED
        '''
        return int(str(self._call('eth_blockNumber')), 16)

