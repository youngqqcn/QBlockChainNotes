## TRON 充币技术实现方案



```


wallet/getnowblock
作用：查询最新块。
demo: curl -X POST  http://127.0.0.1:8090/wallet/getnowblock
参数说明：无
返回值：当前块。


wallet/getblockbynum
作用：通过高度查询块
demo: curl -X POST  http://127.0.0.1:8090/wallet/getblockbynum -d '{"num": 1}'
参数说明：块高度。
返回值：块。


/wallet/gettransactioncountbyblocknum(Odyssey-v3.2开始支持)
作用：查询特定block上transaction的个数
demo: curl -X POST  http://127.0.0.1:8090/wallet/gettransactioncountbyblocknum -d '{"num" : 100}' 
参数说明：num是块的高度.
返回值e：transaction的个数



curl -X POST  http://127.0.0.1:8090/wallet/gettransactionbyid -d '{"value": "d5ec749ecc2a615399d8a6c864ea4c74ff9f523c2be0e341ac9be5d47d7c2d62"}'
参数说明：交易ID。
返回值：交易信息。


```





