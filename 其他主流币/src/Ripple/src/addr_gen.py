#!coding:utf8

#author:yqq
#date:2019/12/5 0005 15:29
#description: 地址生成


from lib.ripple_address import  genb58seed, seed2accid


def main():
    # seed = genb58seed()
    seed = 'ssZ48uwJipMK5xuLjJWWWrUMSE3jr'
    fpgadd, accadd, accid = seed2accid(seed)

    print(seed)
    print('--------------')
    print(accid)


    pass


if __name__ == '__main__':

    main()