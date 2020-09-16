#!coding:utf8

#author:yqq
#date:2020/2/10 0010 11:03
#description: 封装  xlm 代理接口



from stellar_sdk.server import Server
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.network import Network
from stellar_sdk.exceptions import NotFoundError, BadResponseError, BadRequestError

class  XLMProxy(Server):

    # def __init__(self, **kwargs):
    def __init__(self, rpc_host_url : str):
        super(XLMProxy, self).__init__(horizon_url = rpc_host_url)


    def get_account_info(self, straccount : str) -> dict:
        public_key = straccount
        account = self.accounts().account_id(public_key).call()
        return account

    def get_transaction(self, trx_hash : str) -> dict:
        trx_details = self.transactions().transaction(transaction_hash=trx_hash).call()
        return trx_details


    def sendrawtrnasaction(self, tx_xdr_data : str, istestnet : bool ) :
        # networkpharse = Network.PUBLIC_NETWORK_PASSPHRASE if not istestnet else  Network.TESTNET_NETWORK_PASSPHRASE
        # trxv = TransactionEnvelope.from_xdr(xdr=tx_xdr_data, network_passphrase=networkpharse)
        # print(f'len-->{len(tx_xdr_data)}')
        return self.submit_transaction(tx_xdr_data)

