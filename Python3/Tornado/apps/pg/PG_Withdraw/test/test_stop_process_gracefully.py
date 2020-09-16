#!coding:utf8

#author:yqq
#date:2020/6/2 0002 16:18
#description:


import os
from time import sleep
import signal
import sys


def main():

    def on_stop_handler(signum, frame ):
        print(f'signum:{signum}, frame:{frame}')
        print('Exiting application...')
        sys.exit(0)

    def listen_stop_signal():
        signal.signal(signal.SIGINT, on_stop_handler)
        signal.signal(signal.SIGTERM, on_stop_handler)
        # signal.signal(signal.SIGKILL, on_stop_handler)

    def main_loop():
        listen_stop_signal()

        while True:

            sleep(1)
            print(f'Working...PID{os.getpid()}')

    main_loop()



    pass


if __name__ == '__main__':

    main()