#!coding:utf8

#author:yqq
#date:2020/5/21 0021 10:42
#description:
import json
import time

from ed25519 import SigningKey, VerifyingKey




def  sign_msg(sign_key : str, msg : bytes) -> any:
    sk = SigningKey(sk_s=sign_key.encode('latin1'), prefix='', encoding='base64')
    sig = sk.sign(msg=msg, prefix='', encoding='base64')
    return sig


def verify_sig(verify_key : str, sig : str, msg : bytes) -> bool:
    vk = VerifyingKey(vk_s=verify_key, prefix='', encoding='base64')
    try:
        vk.verify(sig=sig, msg=msg, prefix='', encoding='base64')
    except Exception as e:
        return False
    return True



#
# def create_sign_msg(method, url, timestamp, body):
#     params_list = [method, url, timestamp]
#
#     if method == "POST":
#         sorted_body = sorted(body.items(), key=lambda d: d[0], reverse=False)
#         print("sorted_body= ", sorted_body)
#
#         data_list = []
#         for data in sorted_body:
#             if isinstance(data[1], list):
#                 value = "[" + " ".join(data[1]) + "]"
#                 key = data[0]
#                 data_list.append(key + "=" + value)
#             else:
#                 data_list.append("=".join(data))
#
#         body_params = "&".join(data_list)
#         params_list.append(body_params)
#
#     params_str = "|".join(params_list)
#     print("params_str= ", params_str)
#     return params_str


def main():
    ASCCI_VERIFY_KEY = 'WSWAZBS2jty72O5x/2DOTevGwfhPvmXWpclzGWp6M0E'
    ASCCI_SING_KEY = 'n6R1lfDJe5ipiy5KPItTXbMIEu2htV48H0pjPqDgw8A'


    # msg = '{"err_code": 0, "err_msg": null, "timestamp": 1590026959936, "data": {"serial_id": "202005211009196209625", "order_id": "73465774472360"}}'


    data = {
        "pro_id": 3,
        "serial_id": "202005181831579041211"
    }

    jdata = json.dumps(data, separators=(',',':'), sort_keys=True)  #按照key字母顺序排序

    #'1590040704197'
    timestamp = '1590040704197'  #str(int(time.time() * 1000))
    # method  = 'POST'
    url = 'querywithdraworder'

    param = '|'.join([timestamp, url,jdata])
    print(param)

    msg = param.encode('utf8')
    sig = sign_msg(sign_key=ASCCI_SING_KEY, msg=msg)
    print(f'sig:{sig}')
    if verify_sig(verify_key=ASCCI_VERIFY_KEY, sig=sig, msg=msg):
        print('verify ok')
    else:
        print('verify failed')

    pass


if __name__ == '__main__':

    main()