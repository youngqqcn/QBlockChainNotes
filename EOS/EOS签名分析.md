```python
def sig_digest(payload, chain_id=None, context_free_data=None) :
    ''' '''
    if chain_id :
        buf = bytearray.fromhex(chain_id)
    else :
        buf = bytearray(32)
    # already a bytearray
    buf.extend(payload)
    if context_free_data :
        #buf += sha256(context_free_data)
        pass
    else :
        # empty buffer
        buf.extend(bytearray(32))
    return sha256(buf)


def eos_make_raw_transaction():
    ce = eospy.cleos.Cleos(url='http://jungle2.cryptolions.io:80')

    arguments = {
        "from": "yangqingqin1",    #发送账户
        "to": "yangqingqing",      #接收账户
        "quantity": '0.1234 EOS',  #数量
        "memo": "EOS to the moon", #备注
    }
    payload = {
        "account": "eosio.token",  #合约账户
        "name": "transfer",        #方法名
        "authorization": [{        #权限
            "actor": "yangqingqin1",
            "permission": "active",
        }],
    }

    # Converting payload to binary
    data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
    # Inserting payload binary form as "data" field in original payload
    # rsp:{'binargs': '10a6b36c3acba6f1c0a6b36c3acba6f1d20400000000000004454f53000000000f454f5320746f20746865206d6f6f6e'}
    payload['data'] = data['binargs']
    
    # final transaction formed
    trx = {"actions": [payload]}
    
    #交易过期时间, 如果交易在此时间前未被打包, 则视为过期交易
    #最大过期时间可设置1小时
    import datetime as dt
    trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60 * 60)).replace(tzinfo=pytz.UTC))

    print(json.dumps(trx))

    #eospy库的源码是将签名和广播都放在了  push_transaction 中, 
    #这里将交易签名和交易广播两个功能独立出来
    # key = eospy.keys.EOSKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    # resp = ce.push_transaction(trx, key, broadcast=False)
    # print(resp)

    chain_info, lib_info = ce.get_chain_lib_info()
    rawtx = Transaction(trx, chain_info, lib_info)  #广播json的数据
    encoded = rawtx.encode()
    print( "encode: {}".format( encoded) )
    
    #以下是对交易进行序列化(小端), 具体实现见 Transaction.encode()的源码
    # digest 是交易序列化后的sha256哈希值 , digest 也是后面进行ECC签名的输入参数
    # 所谓的交易签名就是digest进行签名
    from eospy.utils import sig_digest
    digest = sig_digest(rawtx.encode(), chain_info['chain_id'])
    print( "digest: {}".format( digest) )

    return rawtx, digest
```





- EOS交易签名的核心代码 

  ```python
  import base58
  import os
  import ecdsa
  import re
  from binascii import hexlify, unhexlify
  import hashlib
  import time
  import struct
  import array
  
  
  
  #重写EOsKey 方便调试
  class MyEosKey( eospy.keys.EOSKey ):
  
      def __init__(self, private_str='') :
        eospy.keys.EOSKey.__init__(self, private_str)
      
      def _check_encode(self, key_buffer, key_type=None) :
          '''    '''
          if isinstance(key_buffer, bytes) :
              key_buffer = key_buffer.decode()
          check = key_buffer
          if key_type == 'sha256x2' :
              first_sha = sha256(unhexlify(check))
              chksum = sha256(unhexlify(first_sha))[:8]   #取前4字节作为校验和
          else :
              if key_type :
                  check += hexlify(bytearray(key_type,'utf-8')).decode()  #将"K1"追加到末尾
              chksum = ripemd160(unhexlify(check))[:8]
          return base58.b58encode(unhexlify(key_buffer+chksum))
  
      def sign_ex(self, digest):
          ''' '''
          cnt = 0
          # convert digest to hex string
          digest = unhexlify(digest)
          if len(digest) != 32:
              raise ValueError("32 byte buffer required")
          while 1:
              
              # get deterministic k
              if cnt:
                  sha_digest = hashlib.sha256(digest + bytearray(cnt)).digest()
              else:
                  sha_digest = hashlib.sha256(digest).digest()
  
              print("sha:{}".format(  hexlify(sha_digest)))
  
              k = ecdsa.rfc6979.generate_k(self._sk.curve.generator.order(),
                                           self._sk.privkey.secret_multiplier,
                                           hashlib.sha256,
                                             # hashlib.sha256(digest + struct.pack('d', time.time())).digest() # use time to randomize
                                           sha_digest
                                           )
              
              # sign the message
              sigder = self._sk.sign_digest(digest, sigencode=ecdsa.util.sigencode_der, k=k)
              
              print('sigder:' + ''.join( [hex(i)[2:]  for i in sigder ]))
  
              # reformat sig
              r, s = ecdsa.util.sigdecode_der(sigder, self._sk.curve.generator.order())
              print("r:{}".format(  hex(r)))
              print("s:{}".format(  hex(s)))
  
              sigder = array.array('B', sigder)
  
              sig = ecdsa.util.sigencode_string(r, s, self._sk.curve.generator.order())
  
              # ensure signature is canonical
              lenR = sigder[3]
              lenS = sigder[5 + lenR]
  
              if lenR == 32 and lenS == 32:
                  # derive recover parameter
                  i = self._recovery_pubkey_param(digest, sig)
                  # compact
                  i += 27
                  # compressed
                  i += 4
                  sigstr = struct.pack('<B', i) + sig
                  print([ i for i in sigstr])
                  break
              cnt += 1
              if not cnt % 10:
                  print('Still searching for a signature. Tried {} times.'.format(cnt))
                  
  
          print( "sigstr:{}".format( hexlify(sigstr)) )
          
          #EOS支持 "secp256k1" 和 "secp256r1"  两个版本的ECC签名
          #这里只讨论  "k1" 版本
          return 'SIG_K1_' + self._check_encode(hexlify(sigstr), 'K1').decode()
  
  
  def eos_sign_raw_transaction(digest):
      key = MyEosKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
      return [ key.sign_ex(digest) ]
      
      
  trx,digest = eos_make_raw_transaction()
  print("digest:{}".format(digest))
  sig = eos_sign_raw_transaction(digest)
  
  #生成广播的json数据
  final_trx = {
          'compression': 'none',
          'transaction': trx.__dict__,
          'signatures': [sig]
  }
  ```

  

- `v1/chain/push_transaction`广播的json数据  

  ```json
  {
  	"compression": "none",
  	"transaction": {
  		"expiration": "2019-09-20T03:56:47.381481+00:00",
  		"ref_block_num": 32953,
  		"ref_block_prefix": 202153414,
  		"net_usage_words": 0,
  		"max_cpu_usage_ms": 0,
  		"delay_sec": 0,
  		"context_free_actions": [],
  		"actions": [{
  			"account": "eosio.token",
  			"name": "transfer",
  			"authorization": [{
  				"actor": "yangqingqin1",
  				"permission": "active"
  			}],
  			"data": "10a6b36c3acba6f1c0a6b36c3acba6f1d20400000000000004454f53000000000f454f5320746f20746865206d6f6f6e"
  		}],
  		"transaction_extensions": []
  	},
  	"signatures": ["SIG_K1_KduPr37mvwWdciVHhUU4g7LCzNDYvVZ4ytxBa8ZhERpycQtn5DrknjcYcedrxbTxuszDHMeCtRbr4aMsLMqFYdTC1c3iqM"]
  }
  ```

  
























