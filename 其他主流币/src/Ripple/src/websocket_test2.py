#!coding:utf8

#author:yqq
#date:2019/12/9 0009 16:49
#description:

import websocket



def main():


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


    recv =  conn.recv()
    print(recv)

    pass


if __name__ == '__main__':

    main()