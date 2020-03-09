#!coding:utf8

#author:yqq
#date:2020/3/4 0004 12:22
#description:




def my_encode_int64( num : int ) -> str:

    # num = 1583290890000

    assert  num > 0

    #原码字符
    raw = bin(num)[2:]
    print(f"原码: {raw}")


    #补码, 因为只处理正数, 所以 补码和原码相同
    complement = raw
    print(f'补码: {complement}')


    #如果长度不是7的倍数, 则补0凑齐
    tmp_complement = complement
    if len(complement) % 7 != 0:
        tmp_complement = '0' * (7 - (len(complement) % 7)) + complement


    print(f'补0后的补码: {tmp_complement}')


    #7位组 , 正序
    seven_bit_array = []
    i = len(tmp_complement) - 1
    tmp = ''
    while i >= 0:
        tmp  =   tmp_complement[i] + tmp
        if i % 7 == 0  :
            seven_bit_array.append(  tmp )
            tmp = ''
        i -= 1

    print(f'正序7位组: { seven_bit_array[::-1] }')
    print(f'反序后7位组: {seven_bit_array}')


    #加上 MSB, 标识位
    added_msb_seven_bit_array = []
    for i in range(0, len(seven_bit_array)):

        #如果是最后一个7位组, 则 MSB标识位是 0,  否则 MSB标识位是 1
        if i == len(seven_bit_array) - 1:
            added_msb_seven_bit_array.append( '0' + seven_bit_array[i] )
        else:
            added_msb_seven_bit_array.append( '1' + seven_bit_array[i] )

    print(f'加上MSB标识位的7位组: {added_msb_seven_bit_array}')


    #最终的 二进制字符串形式
    binstr = ''.join(added_msb_seven_bit_array)
    print(f'最终二进制形式:{binstr}')


    #十六进制字符串形式
    hexstr =  hex( int( binstr, 2  ) )
    print(f'十六进制字符串形式: {hexstr}')

    return hexstr[2:]





def  test_demo():

    my_encode_int64( 1583290890000 )

    print('----------')

    my_encode_int64( 1583290831258 )

    pass




def main():

    test_demo()


    pass


if __name__ == '__main__':

    main()