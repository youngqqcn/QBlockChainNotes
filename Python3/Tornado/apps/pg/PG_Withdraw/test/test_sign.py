#!coding:utf8

#author:yqq
#date:2020/5/22 0022 21:39
#description:  API 签名demo

import json
import time
import requests
from ed25519 import SigningKey, VerifyingKey


def main():
    pg_api_key = 'ad68accaab14a18e15afe21f1330acac5ee3bb4d0c2709443b7d4def89b985bc'
    pg_client_sign_key = '7d9c911ca987e85c90af66511f0ba31ea95996ba7a095b5afcf58df82ae0016c'
    pg_client_verify_key = '77dbfd30dedf746fb6088017cf5fdcbe59411686784bd5a27ca40cef26cab4f7'
    api_url = "http://127.0.0.1:59001/api/demo/this_is_api_name"
    api_name = 'this_is_api_name'

    data = {
        'book':'book name',
        'apple': 'apple name',
        'cat': 'cat name',
        'null_field': None,
        'list_field': ['bbbbb','ccccc','aaaaaa'],
        'object_field':{
            'ccc': '0000',
            'bb': '11111',
            'aaa': '22222'
        },
        'is_ok': True,
    }

    data_json_str = json.dumps(data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序
    print('json_str:{}'.format(data_json_str))

    print('------------------------------\n\n')

    # timestamp_str = str(int(time.time() * 1000))
    timestamp_str = '1590156401029'
    print('tmpstamp_str:{}'.format(timestamp_str))

    print('------------------------------\n\n')
    join_str = '|'.join([timestamp_str, api_name, data_json_str])
    print('join_str:{}'.format(join_str))

    print('------------------------------\n\n')
    sign_msg_bytes = join_str.encode('utf8')
    print('sign_msg_bytes:{}'.format(sign_msg_bytes))

    print('------------------------------\n\n')

    sk = SigningKey(sk_s=pg_client_sign_key.encode('utf8'), prefix='', encoding='hex')
    signature_bytes = sk.sign(msg=sign_msg_bytes, prefix='', encoding='hex')
    print('signature_bytes:{}'.format(signature_bytes))
    print('------------------------------\n\n')

    signature_str = signature_bytes.decode('utf8')
    print('signature_str:{}'.format(signature_str))
    print('------------------------------\n\n')

    req_headers = {
        'ContentType': 'application/json',
        'PG_API_KEY': pg_api_key,
        'PG_API_TIMESTAMP': timestamp_str,
        'PG_API_SIGNATURE': signature_str
    }

    #请求接口
    # rsp = requests.post(url=api_url, json=data, headers=req_headers)

    try:
        vk = VerifyingKey(vk_s=pg_client_verify_key, prefix='', encoding='hex')
        vk.verify(sig=signature_str, msg=sign_msg_bytes, prefix='', encoding='hex')
        print('验签成功')
    except Exception as e:
        print('验签失败')

    pass




def notify_withdraw_to_outer_project( callback_url : str, req_data : dict,
                                      logger, svr_sign_key : str ) :
    """
    提币回调通知统一接口
    :param serial_id:
    :return:
    """
    api_name = 'notifywithdraw'
    # timestamp_str = str(int(time.time() * 1000))
    # data_json_str = json.dumps(req_data, separators=(',', ':'), sort_keys=True)  # 按照key字母顺序排序
    # join_str = '|'.join([timestamp_str, api_name, data_json_str])
    # sign_msg_bytes = join_str.encode('utf8')
    # sk = SigningKey(sk_s=svr_sign_key.encode('utf8'), prefix='', encoding='hex')
    # signature_bytes = sk.sign(msg=sign_msg_bytes, prefix='', encoding='hex')
    # signature_str = signature_bytes.decode('utf8')
    # print('json_str:{}'.format(data_json_str))

    req_headers = {
        # 'ContentType': 'application/json',
        # 'PG_API_KEY': pg_api_key,
        'PG_NOTIFY_TIMESTAMP': 'sfdsdlfkdsjfldskfsfdsfs',
        'PG_NOTIFY_SIGNATURE': 'sdfsdfsdfdsf'
    }

    send_notify_rst = requests.post(url=callback_url, json=req_data, headers=req_headers, timeout=5)
    # logger.info(send_notify_rst)
    # logger.info(f'send_notify_rst:{send_notify_rst.text}')

    # send_notify_rst_text = json.loads(send_notify_rst.text, encoding='utf8')


    # ret_info = NotifyFuncResponse()
    # ret_info.is_notify_successed = False
    #
    # http_status_code = send_notify_rst.status_code
    # if http_status_code == 204 or http_status_code == 200:
    #     ret_info.is_notify_successed = True

    # if send_notify_rst_text["data"]["success"] == True:
    #     ret_info.is_notify_successed = True

    return



if __name__ == '__main__':

    # main()
    url = 'http://192.168.10.155:8001/notify/withdraw'
    # notify_withdraw_to_outer_project(url, {'sdf':'sdfsd'}, None, 'sdfsdfsd')
