"""I want this to be a straightforward and easy to understand
implementation of the signing procedure that can be ripped from this
library and used on its own.

See also:
    https://ripple.com/wiki/User:Singpolyma/Transaction_Signing
"""

import hashlib
from binascii import hexlify
from ecdsa import curves, SigningKey #, six
from ecdsa.util import sigencode_der
from .serialize import (
    to_bytes, from_bytes, RippleBaseDecoder, serialize_object, fmt_hex)


__all__ = ('sign_transaction', 'signature_for_transaction')


tfFullyCanonicalSig = 0x80000000


def sign_transaction(transaction, secret, flag_canonical=True):
    """High-level signing function.hexlify

    - Adds a signature (``TxnSignature``) field to the transaction object.
    - By default will set the ``FullyCanonicalSig`` flag to ``
    """
    if flag_canonical:
        transaction['Flags'] = transaction.get('Flags', 0) | tfFullyCanonicalSig
    sig = signature_for_transaction(transaction, secret)
    transaction['TxnSignature'] = sig
    return transaction


def signature_for_transaction(transaction, secret):
    """Calculate the fully-canonical signature of the transaction.

    Will set the ``SigningPubKey`` as appropriate before signing.

    ``transaction`` is a Python object. The result value is what you
    can insert into as ``TxSignature`` into the transaction structure
    you submit.
    """
    seed = parse_seed(secret)
    key = root_key_from_seed(seed)

    # Apparently the pub key is required to be there.
    transaction['SigningPubKey'] = fmt_hex(ecc_point_to_bytes_compressed(
        key.privkey.public_key.point, pad=True))

    # Convert the transaction to a binary representation
    signing_hash = create_signing_hash(transaction)

    # Create a hex-formatted signature.
    return fmt_hex(ecdsa_sign(key, signing_hash))


def parse_seed(secret):
    """Your Ripple secret is a seed from which the true private key can
    be derived.

    The ``Seed.parse_json()`` method of ripple-lib supports different
    ways of specifying the seed, including a 32-byte hex value. We just
    support the regular base-encoded secret format given to you by the
    client when creating an account.
    """
    assert secret[0] == 's'
    return RippleBaseDecoder.decode(secret)


def root_key_from_seed(seed):
    """This derives your master key the given seed.

    Implemented in ripple-lib as ``Seed.prototype.get_key``, and further
    is described here:
    https://ripple.com/wiki/Account_Family#Root_Key_.28GenerateRootDeterministicKey.29
    """
    seq = 0
    while True:
        private_gen = from_bytes(first_half_of_sha512(
            b''.join([seed, to_bytes(seq, 4)])))
        seq += 1
        if curves.SECP256k1.order >= private_gen:
            break

    public_gen = curves.SECP256k1.generator * private_gen

    # Now that we have the private and public generators, we apparently
    # have to calculate a secret from them that can be used as a ECDSA
    # signing key.
    secret = i = 0
    public_gen_compressed = ecc_point_to_bytes_compressed(public_gen)
    while True:
        secret = from_bytes(first_half_of_sha512(
            b"".join([
                public_gen_compressed, to_bytes(0, 4), to_bytes(i, 4)])))
        i += 1
        if curves.SECP256k1.order >= secret:
            break
    secret = (secret + private_gen) % curves.SECP256k1.order

    # The ECDSA signing key object will, given this secret, then expose
    # the actual private and public key we are supposed to work with.
    key = SigningKey.from_secret_exponent(secret, curves.SECP256k1)
    # Attach the generators as supplemental data
    key.private_gen = private_gen
    key.public_gen = public_gen
    return key


def ecdsa_sign(key, signing_hash, **kw):
    """Sign the given data. The key is the secret returned by
    :func:`root_key_from_seed`.

    The data will be a binary coded transaction.
    """
    r, s = key.sign_number(int(signing_hash, 16), **kw)
    r, s = ecdsa_make_canonical(r, s)
    # Encode signature in DER format, as in
    # ``sjcl.ecc.ecdsa.secretKey.prototype.encodeDER``
    der_coded = sigencode_der(r, s, None)
    return der_coded


def ecdsa_make_canonical(r, s):
    """Make sure the ECDSA signature is the canonical one.

        https://github.com/ripple/ripple-lib/commit/9d6ccdcab1fc237dbcfae41fc9e0ca1d2b7565ca
        https://ripple.com/wiki/Transaction_Malleability
    """
    # For a canonical signature we want the lower of two possible values for s
    # 0 < s <= n/2
    N = curves.SECP256k1.order
    if not N / 2 >= s:
        s = N - s
    return r, s


def get_ripple_from_pubkey(pubkey):
    """Given a public key, determine the Ripple address.
    """
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(pubkey).digest())
    return RippleBaseDecoder.encode(ripemd160.digest())


def get_ripple_from_secret(seed):
    """Another helper. Returns the first ripple address from the secret."""
    key = root_key_from_seed(parse_seed(seed))
    pubkey = ecc_point_to_bytes_compressed(key.privkey.public_key.point, pad=True)
    return get_ripple_from_pubkey(pubkey)


# From ripple-lib:hashprefixes.js
HASH_TX_ID = 0x54584E00; # 'TXN'
HASH_TX_SIGN = 0x53545800  # 'STX'
HASH_TX_SIGN_TESTNET = 0x73747800 # 'stx'

def create_signing_hash(transaction, testnet=False):
    """This is the actual value to be signed.

    It consists of a prefix and the binary representation of the
    transaction.
    """
    prefix = HASH_TX_SIGN_TESTNET if testnet else HASH_TX_SIGN
    return hash_transaction(transaction, prefix)


def hash_transaction(transaction, prefix):
    """Create a hash of the transaction and the prefix.
    """
    binary = first_half_of_sha512(
        to_bytes(prefix, 4) +
        serialize_object(transaction, hex=False))
    return hexlify(binary).upper()


def first_half_of_sha512(*bytes):
    """As per spec, this is the hashing function used."""
    hash = hashlib.sha512()
    for part in bytes:
        hash.update(part)
    return hash.digest()[:256//8]


def ecc_point_to_bytes_compressed(point, pad=False):
    """
    In ripple-lib, implemented as a prototype extension
    ``sjcl.ecc.point.prototype.toBytesCompressed`` in ``sjcl-custom``.

    Also implemented as ``KeyPair.prototype._pub_bits``, though in
    that case it explicitly first pads the point to the bit length of
    the curve prime order value.
    """

    header = b'\x02' if point.y() % 2 == 0 else b'\x03'
    bytes = to_bytes(
        point.x(),
        curves.SECP256k1.order.bit_length()//8 if pad else None)
    return b"".join([header, bytes])


class Test:

    def test_parse_seed(self):
        # To get the reference value in ripple-lib:
        #    Seed.from_json(...)._value.toString()
        parsed = parse_seed('ssq55ueDob4yV3kPVnNQLHB6icwpC')
        assert from_bytes(parsed) == \
               109259249403722017025835552665225484154

    def test_wiki_test_vector(self):
        # https://ripple.com/wiki/Account_Family#Test_Vectors
        seed = parse_seed('shHM53KPZ87Gwdqarm1bAmPeXg8Tn')
        assert fmt_hex(seed) == '71ED064155FFADFA38782C5E0158CB26'

        key = root_key_from_seed(seed)
        assert fmt_hex(to_bytes(key.private_gen)) == \
               '7CFBA64F771E93E817E15039215430B53F7401C34931D111EAB3510B22DBB0D8'

        assert get_ripple_from_pubkey(
            ecc_point_to_bytes_compressed(key.privkey.public_key.point, pad=True)) == \
                'rhcfR9Cg98qCxHpCcPBmMonbDBXo84wyTn'

    def test_key_derivation(self):
        key = root_key_from_seed(parse_seed('ssq55ueDob4yV3kPVnNQLHB6icwpC'))
        # This ensures the key was properly initialized
        expected = '0x902981cd5e0c862c53dc4854b6da4cc04179a2a524912d79800ac4c95435564d'
        if not six.PY3:
            expected = expected + 'L'
        assert hex(key.privkey.secret_multiplier) == expected

    def test_ripple_from_secret(self):
        assert get_ripple_from_secret('shHM53KPZ87Gwdqarm1bAmPeXg8Tn') ==\
               'rhcfR9Cg98qCxHpCcPBmMonbDBXo84wyTn'

    def test_signing_hash(self):
        assert create_signing_hash({"TransactionType": "Payment"}) == \
            b'903C926641095B392A123D4CCD19E060DD8A603C91DDFF254AC9AD3B986C10CF'

    def test_der_encoding(self):
        # This simply verifies that the DER encoder from the ECDSA lib
        # we're using does the right thing and matches the output of the
        # DER encoder of ripple-lib.
        assert hexlify(sigencode_der(
            int('ff89083ed4923b3379381826339c614ac1cb79bf36b18c34d5e97784c5a5a9db', 16),
            int('cc4355eda8ce79c629fb53b0d19abc1b543d9f174626cf33b8a26254c63b22b7', 16),
            None)) == \
            b'3046022100ff89083ed4923b3379381826339c614ac1cb79bf36b18c34d5e97784c5a5a9db022100cc4355eda8ce79c629fb53b0d19abc1b543d9f174626cf33b8a26254c63b22b7'

    def test_canonical_signature(self):
        # From https://github.com/ripple/ripple-lib/blob/9d6ccdcab1fc237dbcfae41fc9e0ca1d2b7565ca/test/sjcl-ecdsa-canonical-test.js
        def parse_hex_sig(hexstring):
            l = len(hexstring)
            r = int(hexstring[:l//2], 16)
            s = int(hexstring[l//2:], 16)
            return r, s

        # Test a signature that will be canonicalized
        input = "27ce1b914045ba7e8c11a2f2882cb6e07a19d4017513f12e3e363d71dc3fff0fb0a0747ecc7b4ca46e45b3b32b6b2a066aa0249c027ef11e5bce93dab756549c"
        r, s = ecdsa_make_canonical(*parse_hex_sig(input))
        assert (r, s) == parse_hex_sig('27ce1b914045ba7e8c11a2f2882cb6e07a19d4017513f12e3e363d71dc3fff0f4f5f8b813384b35b91ba4c4cd494d5f8500eb84aacc9af1d6403cab218dfeca5')

        # Test a signature that is already fully-canonical
        input = "5c32bc2b4d34e27af9fb66eeea0f47f6afb3d433658af0f649ebae7b872471ab7d23860688aaf9d8131f84cfffa6c56bf9c32fd8b315b2ef9d6bcb243f7a686c"
        r, s = ecdsa_make_canonical(*parse_hex_sig(input))
        assert (r, s) == parse_hex_sig(input)

    def test_sign(self):
        # Verify a correct signature is created (uses a fixed k value):
        key = root_key_from_seed(parse_seed('ssq55ueDob4yV3kPVnNQLHB6icwpC'))
        assert hexlify(ecdsa_sign(key, 'FF00EECC', k=3)) == \
            b'3045022100f9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f902205f6d58be6182b9a1e04fcec36f75668deafad2e4336b48770ee5c559d3518301'
