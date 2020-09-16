# -*- coding:utf-8 -*-
"""
author: yqq
date:2019-05-11 18:13
descriptions: USDP 接口
"""

import logging
import json
import warnings

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response

from constants import HTTP_TIMEOUT_SECS

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

MAX_RETRIES = 3


class USDPProxy(object):
    '''
    USDP rpc proxy
    '''

    def __init__(self, host='localhost', port=1317, tls=False):
        self.host = host
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=MAX_RETRIES))




    def _post_json_call(self,  subPath , params):

        data = params
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}/{}'.format(scheme, self.host,  self.port, subPath)
        #print("url:" + url)
        headers = {'Content-Type': "application/json"}
        Response()
        try:
            r = self.session.post(url, headers=headers, data=json.dumps(data), timeout=HTTP_TIMEOUT_SECS)
        except RequestsConnectionError:
            raise BadConnectionError("request  node failed, please contact system administrator to check node server.") #fixed bug, 2019-04-13 yqq
        except Exception as e:
            errMsg = r.text if len(r.text) != 0 else "node server return nothing, maybe your arguments is invalid."
            raise BadConnectionError("%s"% errMsg) 
            
        if r.status_code != 200:
            raise BadStatusCodeError("HTTP%d:%s" %(r.status_code, r.text))
        try:
            return r.text
        except Exception as e:
            raise BadJsonError("error:" + str(r.text))

    def _get_url_call(self, strUrl):
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}/{}'.format(scheme, self.host,  self.port, strUrl)
        #print("url:" + url)
        Response()
        try:
            r = self.session.get(url)
        except RequestsConnectionError:
            raise BadConnectionError("request  node failed, please contact system administrator to check node server.") #fixed bug, 2019-04-13 yqq
        if r.status_code != 200:
            raise BadStatusCodeError(r.status_code)
        try:
            return r.text
        except Exception as e:
            raise BadResponseError("bad response.")
        pass



    #/hs/broadcast
    def sendRawTransaction(self, strRawTxData):
        postData = {"tx" : strRawTxData}
        jsonText = self._post_json_call('hs/broadcast', postData)
        try:
            return json.loads(jsonText)
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))


    #/block_detail/
    def getBlockByBlockNum(self, height):
        jsonText = self._get_url_call("block_detail/"+str(height))
        try:
            return json.loads(jsonText)
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))

    #/auth/accounts/
    def getAccountInfo(self, strAddr):
        jsonText =  self._get_url_call("auth/accounts/" + strAddr)
        try:
            return json.loads(jsonText)
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))


    #/bank/balances
    #return:
    # [{u'denom': u'usdp', u'amount': u'9997987.23'} , {u'denom': u'stake', u'amount': u'149999988'}]
    def getBalance(self, strAddr):
        try:
            jsonText =  self._get_url_call("bank/balances/" + strAddr)
            retList = json.loads(jsonText)
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))
        except BadStatusCodeError:
            return "0"
        
        for item in retList:
            if item["denom"] ==  "usdp" or item["denom"] == "htdf" or item["denom"]=="het":
                return  str(item["amount"])
        return 



    def getLastestBlockNumber(self):
        jsonText = self._get_url_call("blocks/latest")
        try:
            jobj = json.loads(jsonText)
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))

        iHeight = int(jobj["block"]["header"]["height"], 10)
        return iHeight

    def getTxValidInfo(self, strTxid):
        jsonText = self._get_url_call("transaction/" + str(strTxid))
        try:
            txRsp = json.loads(jsonText)
            return txRsp['log'][0]['success'], txRsp['log'][0]['log'] 
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))


    #判断交易的有效性, 因为失败的交易也会被打包进区块  2019-06-13 by yqq
    def isValidTx(self, strTxid):
        jsonText = self._get_url_call("transaction/" + str(strTxid))
        try:
            jobj = json.loads(jsonText)
        except ValueError:
            raise BadJsonError("json error:" + str(jsonText))
        #判断log字段中的success是否是成功
        try:
            strLog = str(json.dumps(jobj["log"])) #2019-07-13 htdf升级之后log改为了json对象
            strLog = strLog.replace(' ', '')
            logging.info(strLog)
            if '"success":true' in strLog: #and 'code' not in jobj:
                return True
            elif '"success":false' in strLog:
                return False
            else:
                return False
        except Exception as e:
            raise BadJsonError("json error:" + str(jsonText))
            
            




        
            




























