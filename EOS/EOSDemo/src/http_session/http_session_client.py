
#!coding:utf8

#author:yqq
#date:2020/1/3 0003 15:09
#description:
import requests
import json
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response


MAX_RETRIES = 3
JSON_MEDIA_TYPE = 'application/json'


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



class EthereumProxy(object):
    '''
    Ethereum JSON-RPC client class
    '''

    DEFAULT_GAS_PER_TX = 90000
    DEFAULT_GAS_PRICE = 50 * 10**9  # 50 gwei

    def __init__(self, host='localhost', port=9000, tls=False):
        self.host = host if host[-1] != '/' else host[:-1]
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=3))

    def _call(self, method, params=None, _id=1):

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
            r = self.session.post(url, headers=headers, data=json.dumps(data), timeout=20)
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


    def get_info(self):
        ret = self._call("get_info", {})
        print(ret)





def main():

    cli = EthereumProxy()
    cli.get_info()



    pass


if __name__ == '__main__':

    main()

