#!coding:utf8

#author:yqq
#date:2020/5/11 0011 10:10
#description:
from binascii import hexlify

from eth_account.datastructures import SignedTransaction
from eth_typing import URI, Address, HexStr, BlockNumber, HexAddress, ChecksumAddress
from eth_utils import to_checksum_address
from web3.exceptions import TimeExhausted
from web3.types import TxReceipt, BlockData

from src.collectors.eth.token_abi.abi import EIP20_ABI
from src.config.constant import ETH_FULL_NODE_RPC_URL, WithdrawStatus, TransferFuncResponse, ETH_CHAIN_ID, \
    ETH_ERC20_GAS_PRICE, ERC20_GAS_LIMIT
# from src.consumers.consumer_base import TransferFuncResponse
from src.config.constant import WithdrawStatus, SubMonitorFuncResponse
from src.lib.exceptions import MqBodyException
# from src.lib.token_abi.abi import EIP20_ABI

from web3 import Web3, HTTPProvider
# from web3.auto import w3

# from src.lib.pg_utils import timestamp_to_datatime
from datetime import datetime

def timestamp_to_datatime(ts : int) -> datetime:
    return datetime.fromtimestamp(ts)




def  sign_and_sendtransaction(myweb3, unsigned_tranaction, private_key : str ) -> TransferFuncResponse:

    signed_tx = myweb3.eth.account.sign_transaction(transaction_dict=unsigned_tranaction, private_key=private_key)
    assert isinstance(signed_tx, SignedTransaction)
    print(hexlify(signed_tx.rawTransaction))

    print(hexlify(signed_tx.hash))

    txhash_ret = myweb3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print( f'tx_hash: {hexlify( txhash_ret)}' )


    rsp = TransferFuncResponse()
    rsp.transaction_status = WithdrawStatus.transaction_status.PENDING  # 广播出去了, 就是pending
    rsp.confirmations = 0
    rsp.block_height = 0
    rsp.tx_hash = '0x' + hexlify(txhash_ret).decode('latin1')  # hexlify(signed_tx.hash)
    # try:
    #     receipt = myweb3.eth.waitForTransactionReceipt(
    #         transaction_hash=txhash_ret,
    #         timeout=1,  # 超时时间 秒 , 没查到就抛异常 web3.exceptions.TimeExhausted
    #         # poll_latency=0.1  # 每隔多少秒 请求一次
    #     )
    #
    #     print(receipt)
    #     # assert isinstance(receipt, TxReceipt)
    #
    #
    #
    #     if receipt['status'] == 1:
    #         rsp.transaction_status = WithdrawStatus.transaction_status.SUCCESS
    #     else:
    #         rsp.transaction_status = WithdrawStatus.transaction_status.FAIL
    #
    #     rsp.block_height = receipt['blockNumber']
    #
    #     block_data = myweb3.eth.getBlock(block_identifier=BlockNumber(rsp.block_height), full_transactions=False)
    #
    #     assert isinstance(block_data, BlockData)
    #     rsp.block_time = timestamp_to_datatime(block_data.timestamp)
    #
    # except TimeExhausted as e:
    #     print(f'{e}')
    #     pass

    return rsp


def  eth_transfer(priv_key : str, from_addr : str,  to_addr : str,  amount : float ) -> TransferFuncResponse:

    myweb3 = Web3(provider=HTTPProvider(endpoint_uri=ETH_FULL_NODE_RPC_URL))
    # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction
    # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction#sign-a-transaction

    from_address = to_checksum_address(from_addr)  #必须使用 checksum addres
    block_identifier = HexStr('pending')
    nonce = myweb3.eth.getTransactionCount(from_address, block_identifier=block_identifier)

    private_key = priv_key
    chksum_to_address = to_checksum_address(to_addr)
    transaction = {
        'to':  to_checksum_address( chksum_to_address) ,   #必须使用 checksum
        'value': Web3.toWei(number=amount, unit='ether'),
        'gas': 21000,
        'gasPrice': Web3.toWei(ETH_ERC20_GAS_PRICE, 'gwei'), # Gwei
        'nonce': nonce,
    }

    print(transaction)

    return sign_and_sendtransaction(myweb3=myweb3, unsigned_tranaction=transaction, private_key=private_key )



def erc20_transfer(priv_key : str, from_addr : str,  contract_addr: str,  token_recipient_addr : str,
                   token_amount : float) \
        -> TransferFuncResponse:


    myweb3 = Web3(provider=HTTPProvider(endpoint_uri=URI(ETH_FULL_NODE_RPC_URL)))

    # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=transaction#sign-a-contract-transaction

    chksum_contract_address = to_checksum_address(contract_addr)

    contract = myweb3.eth.contract(address=chksum_contract_address, abi=EIP20_ABI)

    # name = contract.functions.name().call()
    # print(name)

    symbol = contract.functions.symbol().call()
    print(symbol)

    #判断是否是 USDT
    assert  str(symbol) == 'USDT', 'only support  USDT'

    decimals = contract.functions.decimals().call()
    print(decimals)


    from_address = to_checksum_address(from_addr)
    block_identifier = HexStr('pending')
    nonce = myweb3.eth.getTransactionCount(from_address, block_identifier=block_identifier)

    # assert isinstance(contract.functions, ContractFunctions)
    chksum_token_recipient =  to_checksum_address( token_recipient_addr )
    erc20_unsigned_tx = contract.functions.transfer(
        chksum_token_recipient,
        # !!! 注意 : 只支持 USDT
        myweb3.toWei(token_amount, 'mwei')) \
        .buildTransaction({
        'chainId': ETH_CHAIN_ID,
        'gas': ERC20_GAS_LIMIT,
        'gasPrice': myweb3.toWei(ETH_ERC20_GAS_PRICE, 'gwei'),  #  Gwei
        'nonce': nonce
    })

    print('-----contract_tx----')
    print(erc20_unsigned_tx)

    private_key = priv_key
    return  sign_and_sendtransaction(myweb3=myweb3, unsigned_tranaction=erc20_unsigned_tx, private_key=private_key)

