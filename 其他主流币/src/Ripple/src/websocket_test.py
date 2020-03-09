#!coding:utf8

#author:yqq
#date:2019/12/9 0009 13:49
#description:

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

# def on_open(ws):
#     def run(*args):
#         for i in range(3):
#             time.sleep(1)
#             ws.send("Hello %d" % i)
#         time.sleep(1)
#         ws.close()
#         print("thread terminating...")
#     thread.start_new_thread(run, ())


def on_open(ws):
    def run(*args):
        for i in range(1):
            time.sleep(1)
            # ws.send("Hello %d" % i)
            req_json = """{
  "id": 1,
  "command": "account_channels",
  "account": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
  "destination_account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
  "ledger_index": "validated"
}"""
            ws.send(req_json)



        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("ws://echo.websocket.org/",
    #                           on_message = on_message,
    #                           on_error = on_error,
    #                           on_close = on_close)

    ws = websocket.WebSocketApp('wss://s1.ripple.com/',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()