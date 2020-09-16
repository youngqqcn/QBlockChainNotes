#author: yqq
#date: 2019-12-24
#descriptions: eos rpc proxy

import json
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError



class EosProxy(object):
    def __init__(self,  node_host: str ):
        self.node = node_host

    def __repr__(self):
        return '<EosProxy node=%r>' % self.node


    def _call(self, api_plugin : str , endpoint: str, params: dict) :
        """
        Send request to data API
        :param api_plugin:  plugin_name,  eg. "chain",  "history"
        :param params: query params
        """
        api_uri =  "/v1/" + api_plugin + '/' +  endpoint
        full_url = urljoin(self.node, api_uri)
        data =  json.dumps(params).encode('utf-8')
        req = Request(method='POST', url=full_url, data=data)
        try:
            with urlopen(req, timeout=20) as res:
                res_json = json.loads(res.fp.read().decode('utf-8'))
                return res_json
        except HTTPError as err:
            return {"status": "error", "msg": err}
        except URLError as err:
            return {"status": "error", "msg": err}


    # https://developers.eos.io/eosio-nodeos/reference#get_account
    def chain_get_account(self, account_name : str) -> dict:
        params = { 'account_name' : account_name  }
        retdata = self._call(api_plugin='chain', endpoint='get_account', params=params)
        return  retdata


    #https://developers.eos.io/eosio-nodeos/reference#get_block
    def chain_get_block(self, block_num_or_id : str) -> dict:
        params = {'block_num_or_id' : block_num_or_id}
        retdata = self._call(api_plugin='chain', endpoint='get_block', params=params)
        return  retdata


    #https://developers.eos.io/eosio-nodeos/reference#get_info
    def chain_get_info(self) -> dict:
        params = {}
        retdata = self._call(api_plugin='chain', endpoint='get_info', params=params)
        return  retdata


    #https://developers.eos.io/eosio-nodeos/reference#get_currency_balance
    def chain_get_currency_balance(self, contract_code: str, user_account : str, symbol : str) -> str:
        params = {'code' : contract_code, 'account' : user_account,  'symbol' : symbol }
        retdata = self._call(api_plugin='chain', endpoint='get_currency_balance', params=params)
        return  retdata


    #https://developers.eos.io/eosio-nodeos/reference#push_transaction
    def chain_push_transaction(self):
        pass

    #https://developers.eos.io/eosio-nodeos/reference#get_transaction-1
    def history_get_transaction(self):
        pass

    #https://developers.eos.io/eosio-nodeos/reference#get_actions-1
    def history_get_actions(self):
        pass










