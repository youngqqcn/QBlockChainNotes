#coding:utf8

import decimal
from decimal import Decimal
from decimal import getcontext
from binascii import  unhexlify, hexlify
getcontext().prec = 30

from dateutil import parser
from pytz import timezone

def hex_to_dec(x):
    '''
    Convert hex to decimal
    '''
    return int(x, 16)


def RoundDown(decimalN ):
    decimalFormat = decimalN.quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    return decimalFormat



def hexstr_to_bytes(hexstr : str) -> bytes:
    strtmp  = hexstr.replace('0x', '')
    bytestmp = bytes(strtmp, encoding='latin1')
    return unhexlify(bytestmp)


def timestamp_parse(strtimestamp):
    # 将 UTC时间  转为  当前时区的时间戳
    #'2020-01-03T13:17:48' --- > 1578057468
    return int(parser.parse(strtimestamp).replace(tzinfo=timezone('UTC')).timestamp())




def main():

    pass


if __name__ == '__main__':
    main()
