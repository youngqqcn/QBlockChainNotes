#!coding:utf8

#author:yqq
#date:2020/5/13 0013 20:24
#description:  ETH 和 ERC20代币区块扫描  主程序
from src.scanners.eth_erc20.eth_erc20_scanner_impl import EthErc20ScannerImpl


def main():

    eth_erc20_scanner = EthErc20ScannerImpl()
    eth_erc20_scanner.start_loop()

    pass


if __name__ == '__main__':

    main()