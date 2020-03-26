#!coding:utf8

#author:yqq
#date:2019/12/9 0009 16:49
#description:

import websocket
import json


def demo1():
    conn = websocket.create_connection(url='wss://s.altnet.rippletest.net/', timeout=30)

    req_params = """
        {
      "id": 2,
      "command": "account_info",
      "account": "rpxSrARAeTE2Y699CsY5PwVEJ5v21TDrLi",
      "strict": true,
      "ledger_index": "current",
      "queue": true
    }
        """

    conn.send(payload=req_params)

    recv = conn.recv()
    print(recv)

    pass


def demo2():

    # conn = websocket.create_connection(url='wss://open-api.eos.blockdog.com/v1/ws?apikey=5b4added-e80c-41fb-b5a9-16269d2de79b', timeout=30)
    API_KEY = 'c9c6927a-4784-4f8f-b6a4-65e662ab58ea'
    conn = websocket.create_connection(url='wss://open-api.eos.blockdog.com/v1/ws?apikey={}'.format(API_KEY), timeout=30)
    if not conn.connected :
        print('not connected')
        return
    param = {
        "type": "sub_action_traces",
        "data": {
            "filters": [{
                "account": "eosio.token",
                "name": "transfer",
                "to": "hetbinehpckf"
            }]
        }
    }
    conn.send(payload=json.dumps(param))

    while conn.connected:
    # if True:
        recv = conn.recv()
        print(recv)


    pass

def main():
    # demo1()
    demo2()
    pass


if __name__ == '__main__':

    main()