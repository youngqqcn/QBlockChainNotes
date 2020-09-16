#coding:utf8
#author: yqq
#date: 2019-12-11

import json
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.models import Response

from constants import  XRP_RIPPLED_PUBLIC_API_URL
from constants import  XRP_RIPPLED_PUBLIC_API_PORT

from constants import  HTTP_TIMEOUT_SECS

class RippleProxy(object):
    def __init__(self, host=XRP_RIPPLED_PUBLIC_API_URL, port=XRP_RIPPLED_PUBLIC_API_PORT, tls=True):
        self.host = host if host[-1] != '/' else host[:-1]
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=3))

    def _call(self, method, params=None, _id=1):

        params = params or []
        data = {
            'method': method,
            'params': params,
            'id': _id,
        }
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}'.format(scheme, self.host, self.port)
        headers = {'Content-Type': 'application/json'}
        # Response()
        try:
            r = self.session.post(url, headers=headers, data=json.dumps(data), timeout=HTTP_TIMEOUT_SECS)
        except RequestsConnectionError:
            raise Exception("request ethereum node failed, please contact system administrator to check node server.")  # fixed bug, 2019-04-13 yqq


        if r.status_code / 100 != 2:
            raise Exception(r.status_code)


        try:
            response = r.json()
        except ValueError:
            raise Exception("json error:" + str(r.text))
        try:
            return response['result']
        except KeyError:
            raise Exception(response)


    def get_account_info(self, address : str) -> dict:
        """
        https://xrpl.org/account_info.html
        :param address:
        :return: { 'sequence': 9,  'balance': '12.2342', 'account':address }
        """
        params = {
            "account": "{}".format(address),
            "strict": True,
            "ledger_index": "current",
            "queue": True
        }

        return self._call(method='account_info', params= [params])


    def submit(self, tx_blob : str) -> dict:
        """
        https://xrpl.org/submit.html
        :param tx_blob:
        :return:
        """
        params = {
            "tx_blob": "{}".format(tx_blob)
        }

        return self._call(method='submit', params=[params])

    def transaction_entry(self, tx_hash : str, ledger_index : str) -> dict:
        """
        https://xrpl.org/transaction_entry.html
        :param tx_hash:
        :param ledger_index:
        :return:
        """

        params = {
            "tx_hash": "{}".format(tx_hash),
            "ledger_index" : "{}".format(ledger_index)
        }
        return self._call(method='transaction_entry', params=[params])

    def get_transaction_by_hash(self, tx_hash : str):
        """
        https://xrpl.org/tx.html
        :param tx_hash:
        :return:
        """
        params = {
            "transaction": "{}".format(tx_hash),
            "binary" : False
        }
        return self._call(method='tx', params=[params])



