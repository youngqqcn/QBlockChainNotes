#!encoding:utf8


from ethproxy import EthProxy
import json

#from sql import run
import sql



def main():

    rpc =  EthProxy("192.168.10.199", 18545)
    result  = rpc.eth_getBlockByNumber(4263637)
    #print(type(result))
    #print(len(result))
    print("============================")
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")
    print(result)
    print("")
    print("")
    print("")
    print("")
    print("")
    print("============================")


    #for tx in result:
    #    print("------------")
    #    print(tx)
    #    print("------------")

    print(int(result["number"], 16))
    print(result["hash"])
    #print(int(result["size"], 16))
    print(len(result["transactions"]))


    for item in result["transactions"]:
        print("---------")
        
        jsonStr = json.dumps(item)
        strSql = """insert into json_test(person_desc) VALUES('{0}')""".format(jsonStr)
        #strSql = """insert into json_test(person_desc) VALUES('[{"name":"yqq", "id":999, "amout":9.999999999934}]');"""
        print(strSql)
        #print("strSql:" + strSql)
        sqlRet = sql.run(strSql)
        #print(type(jsonStr))
        #print(jsonStr)
        print(sqlRet)
        print("---------")


    pass



if __name__ == '__main__':
    main()
