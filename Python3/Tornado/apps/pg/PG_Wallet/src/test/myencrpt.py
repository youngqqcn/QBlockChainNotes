#!coding:utf8

#author:yqq
#date:2020/5/29 0029 14:56
#description:

import os
import random
import time


def s() -> bytes:
    x = bytes()
    c = 0
    for n in range(1<<19, 1<<231):
        # if not isprime_fourth(n): continue
        if n % 2 == 0: continue
        t = 0
        u = n - 1
        while u % 2 == 0:
            t += 1
            u //= 2
        a = random.randint(2, n - 1)
        r = pow(a, u, n)
        if r != 1:
            while t > 1 and r != n - 1:
                r = (r * r) % n
                t -= 1
            if r != n - 1: continue
        x += str(n % (1 << 7)).encode('utf-8')
        c += 1
        if c == (1<<8): break
    return x

#加密
def encrypt(path):

    with open(path, 'r') as infile:
        line = infile.readline()
        line = line.strip()
        words_list = line.split(' ')
        if len(words_list) != 12:
            raise RuntimeError('invalid words 无效助记词 !!!')
        for word in words_list:
            if not (word.isalpha() and word.islower()):
                raise RuntimeError('invalid words 无效助记词 !!!')
    x = s()
    fileFullName = path.split(os.path.sep)
    fileParent = path[0:len(path)-len(fileFullName[len(fileFullName)-1])]
    newFileName="x_"+fileFullName[len(fileFullName)-1]
    newFilePath=fileParent+newFileName
    f_read  = open(path,"rb")
    f_write = open(newFilePath,"wb")
    count=0
    buf = bytes()
    for now in f_read:
        for nowByte in now:
            newByte=nowByte^x[count%len(x)]
            count+=1
            f_write.write(bytes([newByte]))
            buf += bytes([newByte])
    f_read.close()
    f_write.close()
    print("文件加密完毕^_^")


def decrypt(path) -> str:
    for ntry in range(100):
        try:
            salt = s()
            f_read = open(path, "rb")
            count = 0
            buf = bytes()
            for now in f_read:
                # time.sleep(3)
                for nowByte in now:
                    newByte = nowByte ^ salt[count % len(salt)]
                    count += 1
                    buf += bytes([newByte])
            f_read.close()

            print(f'salt:{salt}')
            words = buf.decode('utf8')
            words = words.strip()
            words_list = words.split(sep=' ')
            if len(words_list) != 12:
                raise RuntimeError('invalid words 无效助记词 !!!')
            for word in words_list:
                if not (word.isalpha() and word.islower()):
                    raise RuntimeError('invalid words 无效助记词 !!!')
            return words
        except Exception as e:
            print(f'{e}, 继续尝试解密...')
            continue
    raise RuntimeError('解密助记词文件失败!!!!')




def main():

    # v = os.getenv('ENV_NAME')
    #
    # print(v)

    # encrypt('words.txt')
    for i in range(100):
        print(decrypt('x_my_words.dat'))

    pass


if __name__ == '__main__':

    main()