#!coding:utf8

#author:yqq
#date:2019/12/6 0006 15:19
#description:  转账

"""
Example of working with the low-level ripple.client.Client API.
"""
from __future__ import print_function
from queue import Queue, Empty
from ripple.sign import  get_ripple_from_secret  , sign_transaction
from ripple.client import transaction_hash
from ripple.datastructures import Amount


LOCAL_SIGNING = True


def cmd_pay(remote, secret, destination, amount):
    sender = get_ripple_from_secret(secret)
    print('Sender: {}'.format(sender))

    # Construct the basic transaction
    tx = {
        "TransactionType" : "Payment",
        "Account" : sender,
        "Destination" : destination,
        "Amount" : Amount(amount),
    }
    remote.add_fee(tx)

    # We need to determine the sequence number
    sequence = remote.request_account_info(sender)['Sequence']
    tx['Sequence'] = sequence

    # Sign the transaction
    if LOCAL_SIGNING:
        sign_transaction(tx, secret)

    print('I will now submit:')
    # ??? Why does this not work?
    #print(json.dumps(tx, indent=2, cls=RippleEncoder))

    if not LOCAL_SIGNING:
        print(remote.submit(tx_json=tx, secret=secret))
    else:
        # Signup to the transaction stream so we'll be able to verify
        # the transaction result.
        result, queue = remote.subscribe(streams=['transactions'])

        # Submit the transaction.
        remote.submit(tx_blob=tx)
        txhash = transaction_hash(tx)
        print('Submitted transaction with hash %s, waiting for confirm' % txhash)

        # Look for the final disposition.
        # TODO: That would actually involve looking at the values though
        # rather than just printing the first status update.
        while True:
            try:
                tx = queue.get(timeout=1)
            except queue.Empty:
                continue

            if tx['transaction']['hash'] == txhash:
                print('FOUND: %s' % tx)
                break

