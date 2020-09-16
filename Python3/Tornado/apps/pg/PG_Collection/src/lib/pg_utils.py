#!coding:utf8

#author:yqq
#date:2020/5/7 0007 14:13
#description:  工具


import json
import time
import datetime
import decimal
from decimal import Decimal
from typing import Union
from datetime import datetime


def is_valid_url(url : str) -> bool:
    import re
    return None != re.match(r'^https?:/{2}\w.+$', url)


def decimal_to_str(decim : Union[Decimal, float],  precesion : int = 8 ) -> str:
    return str(Decimal(decim).quantize(Decimal('0.' + '0' * precesion)))

def datetime_to_timestamp( dt : datetime  ) -> int:
    return int(time.mktime(dt.timetuple()))


def timestamp_to_datatime(ts : int) -> datetime:
    return datetime.fromtimestamp(ts)



def round_down(decim):
    if isinstance(decim, Decimal):
        decimalFormat = decim.quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    # elif isinstance(decim, int):
    else:
        decimalFormat = Decimal(str(decim)).quantize(Decimal("0.00000000"), getattr(decimal, 'ROUND_DOWN'))
    return decimalFormat

def decimal_default(obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

