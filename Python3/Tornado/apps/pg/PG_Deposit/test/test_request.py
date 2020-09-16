#!coding:utf8

#author:yqq
#date:2020/8/14 0014 19:26
#description:

import requests



def main():

    url = 'http://htdf2020-test01.orientwalt.cn:1317/block_detail/1009408'
    r = requests.get(url=url)
    r.encoding = 'utf8'
    print(r.text)



    pass


if __name__ == '__main__':

    main()