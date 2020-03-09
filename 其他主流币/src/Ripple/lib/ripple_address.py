"""
This script was slapped together very quickly, but just for good measure,
it is licensed under MIT license

Copyright (c) 2014 JMU

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

python-ecdsa library included is also under MIT:
https://github.com/warner/python-ecdsa

"python-ecdsa" Copyright (c) 2010 Brian Warner
Portions written in 2005 by Peter Pearson and placed in the public domain.

"""

import hashlib, sys, time
from  binascii import hexlify, unhexlify

try:
    import ecdsa
except ImportError:
    sys.exit("Error: python-ecdsa does not seem to be installed. Try 'sudo pip install ecdsa'")

curve_order = ecdsa.curves.SECP256k1.order
""" Used in sanity checks """


##################### MISC ######################


def data2int(data):
    """ To compare data as an integer, this helps. """
    # return int(data.encode('hex'), 16)
    nTmp = int(hexlify(data), 16)
    return nTmp


def int2data(int1, padded=0):
    """
    Converts integer into hex data.
    int1 = integer to convert into data
    padded = number of bytes necessary. Will pad msb with 0 bytes. If 0, no padding.
    """
    if type(padded) is not int:
        return None
    padstr = '' if padded <= 0 else '0' + str(padded * 2)
    formatstr = '%' + padstr + 'x'
    hexstr = (formatstr % int1)
    if len(hexstr) % 2 == 1: hexstr = '0' + hexstr
    # return hexstr.decode('hex')
    return  unhexlify(hexstr)


def lines(num):
    """ If Python >3.0 must use print()... TODO """
    for i in range(num):
        print


#################### BASE 58 ####################


__b58chars = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
__b58base = len(__b58chars)
""" This Base58 order is specific to Ripple. Do not use with Bitcoin. """


def b58encode(v):
    """ encode v, which is a string of bytes, to base58."""

    long_value = 0
    for (i, c) in enumerate(v[::-1]):
        long_value += (256 ** i) * c

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    nPad = 0
    for c in v:
        if c == 0:
            nPad += 1
        else:
            break

    return (__b58chars[0] * nPad) + result


def b58decode(v, length):
    """ decode v into a string of len bytes."""
    long_value = 0
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base ** i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]:
            nPad += 1
        else:
            break

    result = chr(0) * nPad + result
    if length is not None and len(result) != length:
        return None

    return result


def EncodeBase58Check(vchIn):
    """ Add checksum and then b58encode vchIn """
    hash = Hash(vchIn)
    return b58encode(vchIn + hash[0:4])


def DecodeBase58Check(psz):
    """
    Validate checksum and return None if invalid.
    Return b58 decoded data SANS CHECKSUM if valid.
    """
    vchRet = b58decode(psz, None)
    strTmp = ''
    for i in vchRet:  strTmp += '%02x' % ord(i)
    print(strTmp)
    vchRet = vchRet.encode('latin1')
    key = vchRet[0:-4]
    csum = vchRet[-4:]
    hash = Hash(key)
    cs32 = hash[0:4]
    if cs32 != csum:
        return None
    else:
        return key


#################### HASHES #####################


def hSHA512(data):
    """ The first half of the SHA512 is used a lot """
    return hashlib.sha512(data).digest()[:32]


def hash_160(public_key):
    """ Same as Bitcoin's SHA256>>RIPEMD160 """
    try:
        md = hashlib.new('ripemd160')
        md.update(hashlib.sha256(public_key).digest())
        return md.digest()
    except Exception:
        import ripemd
        md = ripemd.new(hashlib.sha256(public_key).digest())
        return md.digest()


def Hash(x):
    """ Double SHA256 """
    # if type(x) is unicode: x = x.encode('utf-8')
    if type(x) is str: x = x.encode('utf-8')
    return hashlib.sha256(hashlib.sha256(x).digest()).digest()


################### EC POINTS ###################


def get_point(secret):
    """
    Get Point object from ecdsa.
    secret = String that contains the private key data.
    """
    return ecdsa.keys.SigningKey.from_string(secret, ecdsa.curves.SECP256k1, hashlib.sha256).verifying_key.pubkey.point


def get_pubkey(point, compressed=True):
    """
    Get the Serialized pubkey from an ecdsa Point object.
    point = ecdsa Point object
    compressed = Boolean whether or not you want the pubkey compressed.
    """
    if compressed:
        # return ("0" + str(2 + (1 & point.y())) + ("%064x" % point.x())).decode('hex')
        return unhexlify( bytes("0" + str(2 + (1 & point.y())) + ("%064x" % point.x()), encoding='latin1') )
    else:
        # return ("04" + ("%064x" % point.x()) + ("%064x" % point.y())).decode('hex')
        return unhexlify( bytes("04" + ("%064x" % point.x()) + ("%064x" % point.y()),  encoding='latin1') )


################### ADDRESSES ###################


def data_to_address(data, addrtype=0):
    """
    Add header byte to data, add checksum, then b58encode data.
    data = String of any data.
    addrtype = Int of the number of the header byte in base 10.
    """

    vdata = bytes( chr(addrtype), encoding='latin1') + data
    h = Hash(vdata)
    addr = vdata + h[0:4]
    return b58encode(addr)


def seed2accid(seed, acc=1, subacc=1):
    """
    Generate a Ripple account_id (address) from a Ripple Family Seed.
    seed = String with base58 encoded Ripple "Family Seed".
    acc = Int of the index of the family you want. (Default is 1st family)
    subacc = Int of the index of the account you want. (Default is 1st account)
    ## Note: Look into how families and accounts are used in the real world.
    ##       Currently, it seems most libraries just generate fam 1 acc 1 only.
    """
    dseed = DecodeBase58Check(seed)
    assert dseed != None and dseed[:1] == bytes( chr(33), encoding='latin1' ), 'Invalid Secret'
    seq = 0
    for i in range(acc):
        if i != 0: seq += 1
        fpgsec = hSHA512(dseed[1:] + int2data(seq, 4))
        while data2int(fpgsec) >= curve_order or data2int(fpgsec) <= 1:
            seq += 1
            fpgsec = hSHA512(dseed[1:] + int2data(seq, 4))
    fpgpt = get_point(fpgsec)
    fpgpub = get_pubkey(fpgpt)  # Family Pubkey
    subseq = 0
    for i in range(subacc):
        if i != 0: subseq += 1
        idxsec = hSHA512(fpgpub + int2data(seq, 4) + int2data(subseq, 4))
        while data2int(idxsec) >= curve_order or data2int(idxsec) <= 1:
            subseq += 1
            idxsec = hSHA512(fpgpub + int2data(seq, 4) + int2data(subseq, 4))
    idxpt = get_point(idxsec)
    accpt = fpgpt + idxpt
    accpub = get_pubkey(accpt)  # Account Pubkey
    acc160 = hash_160(accpub)

    fpgadd = data_to_address(fpgpub, 41)  # Family Public Generator
    accadd = data_to_address(accpub, 35)  # Account Public Key
    accid = data_to_address(acc160)  # Account ID (similar to address in Bitcoin)

    return fpgadd, accadd, accid


def genb58seed(entropy=None):
    """
    Generate a random Family Seed for Ripple. (Private Key)
    entropy = String of any random data. Please ensure high entropy.
    ## Note: ecdsa library's randrange() uses os.urandom() to get its entropy.
    ##       This should be secure enough... but just in case, I added the ability
    ##       to include your own entropy in addition.
    """
    if entropy == None:
        entropy = int2data(ecdsa.util.randrange(2 ** 128), 16)
    else:
        entropy = hashlib.sha256(entropy + int2data(ecdsa.util.randrange(2 ** 128), 16)).digest()[:16]
    b58seed = data_to_address(entropy, 33)
    return b58seed