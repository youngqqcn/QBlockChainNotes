#!coding:utf8

#author:yqq
#date:2020/1/13 0013 19:38
#description:

# 基于  EventSource(http长连接) , 而不是Websocket



def main():
    from stellar_sdk.server import Server

    def load_last_paging_token():
        # Get the last paging token from a local database or file
        return "now"

    def save_paging_token(paging_token):
        # In most cases, you should save this to a local database or file so that
        # you can load it next time you stream new payments.
        pass

    # server = Server("https://horizon-testnet.stellar.org")
    server = Server("https://horizon.stellar.org")
    account_id = "GDTIZ3P6L33OZE3B437ZPX5KAS7APTGUMUTS34TXX6Z5BHD7IAABZDJZ"

    # Create an API call to query payments involving the account.
    payments = server.payments().for_account(account_id)

    # If some payments have already been handled, start the results from the
    # last seen payment. (See below in `handle_payment` where it gets saved.)
    last_token = load_last_paging_token()
    # if last_token:
    #     payments.cursor(last_token)

    # `stream` will send each recorded payment, one by one, then keep the
    # connection open and continue to send you new payments as they occur.
    #  基于  EventSource(http长连接) , 而不是Websocket
    for payment in payments.stream():
        # Record the paging token so we can start from here next time.
        save_paging_token(payment["paging_token"])
        from pprint import pprint
        pprint(payment)

        # We only process `payment`, ignore `create_account` and `account_merge`.
        if payment["type"] != "payment":
            continue

        # The payments stream includes both sent and received payments. We
        # only want to process received payments here.
        if payment['to'] != account_id:
            continue

        # In Stellar’s API, Lumens are referred to as the “native” type. Other
        # asset types have more detailed information.
        if payment["asset_type"] == "native":
            asset = "Lumens"
        else:
            asset = f"{payment['asset_code']}:{payment['asset_issuer']}"
        print(f"{payment['amount']} {asset} from {payment['from']}")

        #获取更多信息  memo_type  和 memo
        ret = server.transactions().transaction( payment['transaction_hash'] ).call()
        from pprint import pprint
        pprint(ret)



    pass


if __name__ == '__main__':

    main()