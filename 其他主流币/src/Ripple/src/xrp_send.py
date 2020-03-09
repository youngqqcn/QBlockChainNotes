#!coding:utf8

#author:yqq
#date:2019/12/9 0009 14:29
#description:

from lib.ripple import Remote
from lib.ripple import Client
from pprint import  pprint

from lib.ripple.client import get_ripple_from_secret
from lib.ripple.sign import  sign_transaction
from lib.ripple.client import transaction_hash
from lib.ripple.datastructures import Amount
from lib.ripple.serialize import serialize_object

import  queue as Queue

#
#
# def main():
#
#
#     # cli =  Client('wss://s1.ripple.com/')
#
#     remote = Remote(url='wss://s.altnet.rippletest.net/', secret='ssYt3QxVJtAqtw88REsc7S7X3mHrZ')
#
#     rsp = remote.send_payment(destination='snTru9VEkoQNwRoKTJzNDVg2TDgQk',
#                         amount=5,
#                         destination_tag=55551)
#
#     pprint(rsp)
#
#
#
#
#     pass
#
#
# if __name__ == '__main__':
#
#     main()







def main():
    LOCAL_SIGNING = True

    # def cmd_pay(remote, secret, destination, amount):
    if True:

        secret = 'ssYt3QxVJtAqtw88REsc7S7X3mHrZ'
        # remote = Remote(url='wss://s.altnet.rippletest.net/', secret=secret)
        remote = Client(url='wss://s.altnet.rippletest.net/')
        destination = 'rBQUkC3iBBAXV7XT4DJeCPiMHQM6PVE555'
        amount = 5


        sender = get_ripple_from_secret(secret)
        print('Sender: {}'.format(sender))

        # Construct the basic transaction
        tx = {
            "TransactionType": "Payment",
            "Account": sender,
            "Destination": destination,
            "Amount": Amount(amount),
        }
        remote.add_fee(tx)

        # We need to determine the sequence number
        print('--------request_account_info------------')
        sequence = remote.request_account_info(sender)['Sequence']
        tx['Sequence'] = sequence
        # tx['Sequence'] = 1
        tx_blob = serialize_object(tx)

        # Sign the transaction
        if LOCAL_SIGNING:
            sign_transaction(tx, secret)

        print('I will now submit:')
        # ??? Why does this not work?
        # print(json.dumps(tx, indent=2, cls=RippleEncoder))

        tx_blob = serialize_object(tx)
        pprint( tx_blob )
        # return


        if not LOCAL_SIGNING:
            print(remote.submit(tx_json=tx, secret=secret))
        else:
            # Signup to the transaction stream so we'll be able to verify
            # the transaction result.
            result, queue = remote.subscribe(streams=['transactions'])

            # Submit the transaction.
            remote.submit(tx_blob=tx)
            txhash = transaction_hash(tx)

            txhash = txhash.decode('latin1')

            # print(type(txhash))
            print('Submitted transaction with hash %s, waiting for confirm' % txhash)

            # Look for the final disposition.
            # TODO: That would actually involve looking at the values though
            # rather than just printing the first status update.
            while True:
                try:
                    tx = queue.get(timeout=1)
                except Queue.Empty:
                    continue

                hash =  tx['transaction']['hash']
                # print( type(hash) )


                # break
                if hash == txhash:
                    print('FOUND: ' )
                    pprint(tx)
                    break


    pass


if __name__ == '__main__':

    main()