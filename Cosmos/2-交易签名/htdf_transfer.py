#!coding:utf8

#author:yqq
#date:2019/5/6 0006 18:07
#description:



import json
import hashlib
import coincurve
import base64
from collections import OrderedDict

def ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        # v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]

        return r, s



    pass




import requests

g_addr_file_path = './htdf_addr.txt'
g_node_ip_port = '47.88.173.14:1317'   #节点ip和端口

g_strFrom = 'htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2'
g_PrivKey = '485de9a2ee4ed834272389617da915da9176bd5281ec5d261256e15be0c375f2'
g_PubKey = '0329cdc2270b26983d492ca88d7434e2f19c7760d87b8ebadf29d016b939329e9d'
g_gas = 200000  #默认即可
g_fee =  20  #默认即可

def Transfer(strFrom, strTo, nAmount):

    try:
        rsp =  requests.get('http://%s/auth/accounts/%s' % (g_node_ip_port.strip(), strFrom.strip()))
        rspJson = rsp.json()
        nAccountNumber = int(rspJson['value']['account_number'], 10)
        nSequence = int(rspJson['value']['sequence'], 10)

    except Exception as e:
        print (e)
        return

    print('account_number : %d' % nAccountNumber)
    print('sequence: %d' % nSequence)


    print('\n-----------------------------------\n')


    jUnTxStr = """{\
    "account_number": "%d",\
	"chain_id": "mainchain",\
	"fee": {\
		"amount": [{\
			"amount": "%d",\
			"denom": "satoshi"\
		}],\
		"gas": "%d"\
	},\
    "memo": "",\
	"msgs": [{\
		"Amount": [{\
			"amount": "%d",\
            "denom": "satoshi"\
		}],\
		"From": "%s",\
		"To": "%s"\
	}],\
    "sequence": "%d"\
}"""  % (nAccountNumber, g_fee, g_gas, nAmount, strFrom, strTo , nSequence)

    # jUnTxStr = json.dumps(jUnTx , sort_keys=False)
    jUnTxStr = jUnTxStr.replace(' ', '')
    jUnTxStr = jUnTxStr.replace('\t', '')
    jUnTxStr = jUnTxStr.replace('\n', '')
    print(jUnTxStr)



    # return

    print("json字符转为byteArray: ")
    for  i in bytearray(jUnTxStr):
        # print('{0}'.format(chr(i))),
        print('{0}({1}),'.format(i, chr(i))),
    shaData =  hashlib.sha256( bytearray(jUnTxStr) ).digest()
    print('\n-----------------------------------\n')
    print("Json的sha256结果:")
    print(shaData.encode('hex'))
    privKey = g_PrivKey.decode('hex')

    print('\n--------------------------------------\n')
    print("strPrivKey:", privKey.encode('hex'))
    r, s = ecsign(shaData,  privKey)
    print('r:' + r.encode('hex'))
    print('s:' + s.encode('hex'))

    print('\n--------------------------------------\n')
    b64Data = base64.b64encode(r + s)
    print(b64Data)

    print('--------------------------------------')
    pubKey = g_PubKey
    b64PubKey = base64.b64encode(pubKey.decode('hex'))
    print("公钥的base64编码:" + b64PubKey)



    #---------------------------------------------------------

    jSigTx = """{
        "type": "auth/StdTx",
        "value":{
            "msg": [{
                "type": "htdfservice/send",  
                "value":{
                    "From": "%s",
                    "To": "%s",
                    "Amount": [{
                        "denom": "satoshi",
                        "amount": "%d"
                    }]
                }
            }],
            "fee": {
                "amount": [{
                    "denom": "satoshi",
                    "amount": "%d"
                }],
                "gas": "%d"
            },
            "signatures": [{
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "%s"
                },
                "signature": "%s"
            }],
            "memo": ""
        }
    }""" %(strFrom, strTo , nAmount, g_fee, g_gas, b64PubKey, b64Data)

    jSigTxStr = jSigTx
    jSigTxStr = jSigTxStr.replace(' ', '')
    jSigTxStr = jSigTxStr.replace('\t', '')
    jSigTxStr = jSigTxStr.replace('\n', '')
    bcastData = jSigTxStr.encode('hex')
    print("签名的json:" + jSigTxStr)
    print("签名后的交易:"+ bcastData)


    # return

    #------------------------进行广播-----------------------------------
    import json
    bcastData = {'tx' :  bcastData }
    postData = json.dumps(bcastData)
    rsp = requests.post('http://%s/hs/broadcast' % (g_node_ip_port),  postData)

    try:
        if rsp.status_code == 200:
            rspJson = rsp.json()
            txid = str(rspJson['txhash'])
            print("%s 转给 %s 金额: %d  的交易广播成功, txid:%s" % (strFrom, strTo , nAmount, txid))
        else:
            print("广播失败: %s " % str(rsp.text))
            return
            # print("%s 转给 %s 金额: %d  的交易广播广播失败: %s" % (strFrom, strTo , nAmount, rsp.text))
    except Exception as e:
        print(e)
        return


def ReadAddrFile(strFilePath):
    retMap = {}
    with open(strFilePath) as inFile:
        lines = inFile.readlines()
        for line in lines:
            splits =  line.split('\t')
            if len(splits) == 2:
                retMap[str(splits[0]).strip()] = int(str(splits[1]).strip(), 10) * (10**8)
    return retMap





if __name__ == '__main__':

    import time
    txMap  = ReadAddrFile(g_addr_file_path)
    # print(txMap)

    for key in txMap:
        time.sleep(5)
        Transfer(g_strFrom, key , txMap[key])
        time.sleep(5)

        break
