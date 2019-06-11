#! coding:utf8

from  proxy import USDPProxy  




def main():
    print("starting test.....")

    px = USDPProxy("192.168.10.23")
    
    ret = ""
    try:
        ret = px.newaccount("12345678")
        print(ret)
    except BaseException as e:
        print(e)

    try:
        ret = px.newaccount("123456734234234234234klkfjslsfjslfjsdfl8")
        print(ret)
    except BaseException as e:
        print(e)

    pass

def main2():
    print("starting test.....")

    px = USDPProxy("192.168.10.23")
    
    ret = ""
    try:
        ret = px.getBlockByBlockNum(20531)
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print("error")

    try:
        ret = px.getBlockByBlockNum(205334241)
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print("error")

    pass


def main3():
    print("starting test.....")

    px = USDPProxy("192.168.10.23")
    
    ret = ""
    try:
        ret = px.getAccountInfo("usdp1d7xsdldypy0k8khw59p2hvr8378c3vd8p5c0qf")
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print(e)
        print("error")

    try:
        ret = px.getAccountInfo("usdp1d7xsdldypy0k8khw59p2hvr8378c3vd8p5c0qh")
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print(e)
        print("error")

    pass

def main4():
    print("starting test.....")

    px = USDPProxy("192.168.10.23")
    
    ret = ""
    try:
        ret = px.getBalance("usdp1d7xsdldypy0k8khw59p2hvr8378c3vd8p5c0qf")
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print(e)
        print("error")

    try:
        ret = px.getBalance("usdp1d7xsdldypy0k8khw59p2hvr8378c3vd8p5c0qh")
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print(e)
        print("error")

    pass

def main5():
    print("starting test.....")

    px = USDPProxy("192.168.10.23")
    
    ret = ""
    try:
        ret = px.getLastestBlockNumber()
        print("------------------")
        print(type(ret))
        print(ret)
    except BaseException as e:
        print("------------------")
        print(e)
        print("error")



if __name__ == '__main__':

    '''
    main()
    main2()
    main3()
    main4()
    '''
    main5()

