#!coding:utf8

#author:yqq
#date:2020/1/13 0013 19:34
#description:


from stellar_sdk.keypair import Keypair
from stellar_sdk.network import Network
from stellar_sdk.server import Server
from stellar_sdk.transaction_builder import TransactionBuilder
from stellar_sdk.exceptions import NotFoundError, BadResponseError, BadRequestError

def main():


    # server = Server("https://horizon-testnet.stellar.org")
    server = Server("https://horizon.stellar.org")
    # source_key = Keypair.from_secret("SARJMVBEUC32ITKBIBYRQZUFEWKYHMR7PET5NDZH6KPREY3CPCUQSBJU")  #test1
    # destination_id = "GBMHN7DQ7MQTFPUPAYJR6HUGI2WX55LDTJ4AJNBQPIWMHNHSN34A2ENS"  #test2

    # test2
    # Secret: SARJMVBEUC32ITKBIBYRQZUFEWKYHMR7PET5NDZH6KPREY3CPCUQSBJU
    # Public Key: GDTIZ3P6L33OZE3B437ZPX5KAS7APTGUMUTS34TXX6Z5BHD7IAABZDJZ

    source_key = Keypair.from_secret("SARJMVBEUC32ITKBIBYRQZUFEWKYHMR7PET5NDZH6KPREY3CPCUQSBJU")
    # destination_id = "GC2QRLQCNCIK3FEIPEO7KP64PBOTFREGNCLMUG64QYOQFVQVARQCNPTV"
    destination_id = "GDKSN4MKI3VCX4ZN6P6WVQR64TGKPOHPKVBCO5ERJABMHI7GJHNAF6PX"

    #如果目的账户不存在, 则使用  append_create_account_op
    #如果目的账号存在, 则使用 append_payment_op
    # First, check to make sure that the destination account exists.
    # You could skip this, but if the account does not exist, you will be charged
    # the transaction fee when the transaction fails.

    is_acc_exits = False
    try:
        server.load_account(destination_id)
        is_acc_exits  = True
    except NotFoundError:
        # If the account is not found, surface an error message for logging.
        # raise Exception("The destination account does not exist!")
        print(f"{destination_id} not found, will create it")
        is_acc_exits = False

    # If there was no error, load up-to-date information on your account.
    source_account = server.load_account(source_key.public_key)

    # Let's fetch base_fee from network
    base_fee = server.fetch_base_fee()

    # Start building the transaction.

    txbuilder = TransactionBuilder(
            source_account=source_account,
            # network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
            base_fee=base_fee,
        )


    if is_acc_exits:
        txbuilder.append_payment_op(destination=destination_id, amount="1.6666", asset_code="XLM")
    else:
        txbuilder.append_create_account_op(destination=destination_id, starting_balance="1.001")

    txbuilder.add_text_memo("101108")\
            .set_timeout(1000)


    transaction = txbuilder.build()

    # transaction = (
    #     TransactionBuilder(
    #         source_account=source_account,
    #         # network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
    #         network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
    #         base_fee=base_fee,
    #     )
    #         # Because Stellar allows transaction in many currencies, you must specify the asset type.
    #         # Here we are sending Lumens.
    #         # .append_payment_op(destination=destination_id, amount="1.001", asset_code="XLM")
    #         .append_create_account_op(destination=destination_id, starting_balance="1.001")
    #         # A memo allows you to add your own metadata to a transaction. It's
    #         # optional and does not affect how Stellar treats the transaction.
    #         .add_text_memo("556850")
    #         # Wait a maximum of three minutes for the transaction
    #         .set_timeout(10)
    #         .build()
    # )

    # Sign the transaction to prove you are actually the person sending it.
    transaction.sign(source_key)


    print(f'xdr trx: {transaction.to_xdr()}')

    xdr = transaction.to_xdr()
    print(f'len : {len(xdr)}')
    print(type(server))
    # rsp = server.submit_transaction(xdr)
    # print(rsp)

    try:
        # And finally, send it off to Stellar!
        response = server.submit_transaction(transaction)
        print(f"Response: {response}")
    except (BadRequestError, BadResponseError) as err:
        print(f"Something went wrong!\n{err}")



    pass


if __name__ == '__main__':

    main()