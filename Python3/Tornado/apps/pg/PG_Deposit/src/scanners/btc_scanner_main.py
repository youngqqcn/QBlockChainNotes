#!coding:utf8

#author:yqq
#date:2020/7/10 0010 10:28
#description:  BTC区块扫描主函数
from src.config.constant import BTC_API_HOST, BTC_API_PORT
from src.scanners.btc.btc_scanner_impl import BtcScannerImpl



def main():

    btc_scanner = BtcScannerImpl(btc_api_host=BTC_API_HOST, btc_api_port=BTC_API_PORT)
    btc_scanner.start_loop()

    pass


if __name__ == '__main__':

    main()