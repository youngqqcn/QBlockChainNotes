#!coding:utf8

#author:yqq
#date:2020/1/13 0013 15:51
#description: 生成密钥对



from stellar_sdk.keypair import Keypair

def main():

    kp = Keypair.random()
    print("Secret: {}".format(kp.secret))
    print("Public Key: {}".format(kp.public_key))
    print("")

    pass


if __name__ == '__main__':

    main()