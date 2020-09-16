#!coding:utf8

#author:yqq
#date:2020/5/14 0014 11:08
#description:  HTDF 区块扫描主函数
from src.scanners.htdf.htdf_scanner_impl import HTDFScannerImpl


def main():

    eth_erc20_scanner = HTDFScannerImpl()
    eth_erc20_scanner.start_loop()

    pass


if __name__ == '__main__':

    main()