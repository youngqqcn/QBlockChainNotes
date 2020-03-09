#!coding:utf8

#author:yqq
#date:2020/1/13 0013 18:11
#description:



from pprint import pprint

def main():
    from stellar_sdk.server import Server

    server = Server("https://horizon-testnet.stellar.org")
    public_key = "GDTIZ3P6L33OZE3B437ZPX5KAS7APTGUMUTS34TXX6Z5BHD7IAABZDJZ"
    account = server.accounts().account_id(public_key).call()

    pprint(account)

    for balance in account['balances']:
        print(f"Type: {balance['asset_type']}, Balance: {balance['balance']}")



    pass


if __name__ == '__main__':

    main()