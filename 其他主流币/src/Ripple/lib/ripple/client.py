from __future__ import unicode_literals
try:
    from queue import Queue, Empty
except ImportError:
    # Python 2
    from Queue import Queue, Empty
from decimal import Decimal
import json
import threading
import websocket
import logging
from lib.ripple import Amount
from lib.ripple.serialize import serialize_object
from lib.ripple.sign import hash_transaction, HASH_TX_ID, get_ripple_from_secret, sign_transaction
from pprint import  pprint


__all__ = ('Remote', 'Client', 'RippleError')


log = logging.getLogger('ripple.client')
log.addHandler(logging.NullHandler())


class RippleError(Exception):
    pass


class ResponseError(RippleError):
    def __init__(self, error_response):
        self.response = error_response
        RippleError.__init__(
            self,
            error_response.get('error_exception',
                               error_response.get('error_message', '')))

    def __getitem__(self, item):
        return self.response[item]


class TransactionError(ResponseError):
    """Respresents an error in a transaction. A transaction is a
    higher-level object of our own. For example, the ripple server
    may give us a temporary "tes*" response, and we continue to wait
    and confirm until we have a final answer. Only then do we complete
    or fail our transaction.
    """
    def __init__(self, error_code, full_response):
        self.response = full_response
        RippleError.__init__(
            self,
            full_response.get('error_exception',
                               full_response.get('error_message', '')))

    def __getitem__(self, item):
        return self.response[item]


FEE_DEFAULTS = {
    'fee_ref': 10,       # cost of reference transaction in "fee units"
    'fee_base': 10,      # cost of reference transactios in XRP
    'load_base': 256,
    'load_factor': 256,
    'base_fee': 10       # default cost of a transaction in units
}


class RippleEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


def transaction_hash(tx_json):
    """To identify a transaction, we can use the signing-hash algorithm
    with a special prefix; the result should match the transaction id
    that the server will use.

    In particular because we do not have a blob serializer, we'll have to
    use the dict structure to calculate the hash.
    """
    return hash_transaction(tx_json, HASH_TX_ID)


class DeferredResponse(object):
    """A future that can either return a result value or raises
    an exception.

    - Must be resolved with a ripple server response, or an exception
      instance.
    - If the response indicates an error, will throw a ResponseError.
    - If resolved with an exception instance, will throw that.
    - Otherwise will resolve the the ripple server response.
    """
    def __init__(self):
        self.resolved = threading.Event()
        self.response = None
        self.resulter = None

    def wait(self, timeout=None):
        self.resolved.wait(timeout)

        if isinstance(self.response, Exception):
            raise self.response

        if not self.response['status'] == 'success':
            raise ResponseError(self.response)
        result = self.response['result']
        if self.resulter:
            result = self.resulter(result)
        return result

    def resolve(self, response):
        self.response = response
        self.resolved.set()


class SubscriptionQueue(Queue):

    def get(self, block=True, timeout=None):
        result = Queue.get(self, block, timeout)
        if isinstance(result, Exception):
            raise result
        return result



class Client(object):
    """Connection to Ripple network.

    This is supposed to be more of a low-level API, representing
    a single connection. You'll have to handle errors manually.

    It uses a thread internally, and is itself threadsafe. Subscriptions
    return a queue that can be read from.

    Some notes on the design
    ------------------------

    I still haven't grogged how to do network APIs. I think my confusion
    stems from the desire to enable both blocking and non-blocking use
    cases, hating threads, nor wanting to rely on greenlets.

    Here are some things that were considered:

    1. Expose a Deferred object to the user. This feels like re-inventing
       Twisted (up to API methods needing to inject code "on success" to
       fetch the desired data from the result structure).
       This approach means the user has an async-interface within a single
       thread of his own, which seems a waste considering we only have
       a single websocket connection to begin with.

    2. Keep the wait() internal, the external API methods block until a
       result is available. Makes for a nice sync API while still letting
       the user use multiple threads if he so desires (like handling the
       results of a subscribe). This is what we are doing now.

    3. Use no thread thread at all, not allowing async usage. That
       means the user has to clear subscription messages in this main
       thread in between regular interactions. I felt this would be too
       restrictive.

    4. Do not use an internal thread but still support async usage. I
       believe this to be possible along the lines of this pseudo code::

           def consume_one(self):   # read subscription messages
                dispatch_queue_first
                with self.recv_lock:
                    msg = self.conn.recv(block=False)
                    dispatch_queue_again
                    if msg: dispatch_msg(triggers command wait() events)

            def wait(self, id):
                check_queue_first
                with self.recv_lock:
                    check_queue_again
                    receive_and_add_to_queue(until msg with id found)

        The downside: while waiting for one response, all other readers
        are blocked, even if a response for their command has come in.
        Given that responses should generally be immediate, presumably
        this isn't that big a deal. Still, it felt a bit hacky.


    How should subscriptions be handled? In general, when a thread is
    used, we'd either have to do the callback from the thread, which
    sucks, or, what I'm doing know, giving the consumer a queue which
    he'll have to read from at his convenience.
    """
    # TODO: Better handle keyboard interrupts while waiting:
    #    http://stackoverflow.com/a/14421297/15677

    def __init__(self, url):
        self.fee_info = FEE_DEFAULTS.copy()

        # These will be used to sync the reading thread with the threads
        # that are consuming us. Yes, single dict and lock could be used,
        # but when setting up a subscription we need to wait for a server
        # ok but can't miss a message afterwards, so a separate lock
        # allows us to block incoming subscriptions update while still
        # setting up the callback queue.
        self.callbacks = {}
        self.subscriptions = {}
        self.callbacks_lock = threading.RLock()
        self.subscriptions_lock = threading.RLock()

        # TODO: We need to deal with timeouts (a ping thread?)
        self.conn = websocket.create_connection(url, timeout=30)
        # self.conn = websocket.WebSocket()
        # This thread will do the reading in the basis for in turn
        # supporting multiple threads to use *this* class.
        self._read_thread = thread = threading.Thread(target=self._read_proc)
        thread.setDaemon(True)
        thread.start()

    def close(self):
        log.debug('client.close()')
        self._shutdown = True
        self.conn.close()

    def _mkid(self):
        setattr(self, '_id', getattr(self, '_id', 0) + 1)
        return self._id

    def _read_proc(self):
        """Runs the reading thread."""
        try:
            while not getattr(self, '_shutdown', False):
                print("-----------readproc--------------")
                # msg = json.loads(self.conn.recv().decode('utf-8'))
                recv = self.conn.recv()
                # print(recv)
                if isinstance(recv, str):
                    msg = json.loads(recv)
                    log.debug('<<<<<<<< receiving % s', json.dumps(msg, indent=2))
                elif isinstance(recv, bytes):
                    msg  = recv
                else:
                    raise  ValueError("error response format, must be valid json")

                # msg = json.loads(self.conn.recv().decode('utf-8'))
                # print('<<<<<<<< receiving % s', json.dumps(msg, indent=2))

                # print('======receiving======')
                # pprint(msg)
                # print('=====================')

                type = msg['type']

                # Response to a regular command
                if type == 'response':
                    with self.callbacks_lock:
                        if msg['id'] in self.callbacks:
                            self.callbacks[msg['id']].resolve(msg)
                            continue

                # Else this will be a subscription response
                with self.subscriptions_lock:
                    if type in self.subscriptions:
                        # Multiple subscriptions may have been issued for
                        # the same type, notify all of them.
                        for queue in self.subscriptions[type]:
                            queue.put(msg)
                        continue

                raise ValueError(
                    'unexpected message from server: %s' % str(msg))
        except Exception as e:
            # If we have already shutdown, ignore the error. This is
            # because by shutting down the socket during a recv(), a
            # variety of socket-related / SSL errors are to be expected.
            if not getattr(self, '_shutdown', False):
                # Notify all callbacks so that exceptions occur
                # in all waiters.
                with self.callbacks_lock:
                    for deferred in self.callbacks.values():
                        deferred.resolve(e)
                with self.subscriptions_lock:
                    for queues in self.subscriptions.values():
                        for queue in queues:
                            queue.put(e)
                # Also shut down the connection so that the main thread
                # doesn't keep sending while not getting a response.
                self.conn.close()
                # Finally, re-raise the exception in the thread
                raise
        log.debug('client.read_proc now shut down')

    def execute(self, cmd, **data):
        """Send a commad to the server, wait for the result. Sync!

        Possible outcomes are from DeferredResponse.wait(): A ripple
        server response or an ResponseError exception.
        """
        # Prepare the command to send
        data['command'] = cmd
        data['id'] = self._mkid()
        data = {k:v for k, v in data.items() if v is not None}

        log.debug('>>>>>>>> sending %s', json.dumps(data, indent=2, cls=RippleEncoder))
        self.conn.send(json.dumps(data, cls=RippleEncoder).encode('utf-8'))
        with self.callbacks_lock:
            self.callbacks[data['id']] = DeferredResponse()
        msg = self.callbacks[data['id']].wait()
        return msg

    def subscribe(self, streams=None):
        def add_queue(name, queue):
            queues = self.subscriptions.setdefault(name, [])
            queues.append(queue)

        with self.subscriptions_lock:
            result = self.execute('subscribe', streams=streams)
            self._process_fee_update(result)
            # Setup a queue for subscription messages
            queue = SubscriptionQueue()
            for stream in streams:
                if 'ledger' == stream:
                    add_queue('ledgerClosed', queue)
                elif 'transactions' == stream:
                    add_queue('transaction', queue)
                elif 'server' == stream:
                    add_queue('serverStatus', queue)
                # elif 'transactions_proposed' == stream:
                #     add_queue('transactions_proposed', queue)
                else:
                    raise ValueError(stream)

        return result, queue

    def add_fee(self, tx, amount=None, cushion='1.2'):
        """Add a fee to the given transaction dict.
        """
        if not amount:
            # https://ripple.com/wiki/Transaction_Fee#Calculating_the_Transaction_Fee
            # https://ripple.com/wiki/Calculating_the_Transaction_Fee
            # Note: The ripple client uses a design where every transaction
            # may have a different cost in fee units, but then just uses
            # 10 as a default. We'll ignore it.
            D = Decimal
            i = lambda k: D(self.fee_info[k])
            # One fee unit in XRP
            one_unit = i('fee_base') / i('fee_ref')
            # Therefore the cost =
            fee = one_unit * i('base_fee')
            # Consider the load
            fee = fee * (i('load_factor') / i('load_base'))
            # Add a safety cushion
            amount = int(fee * D(cushion))
        tx['Fee'] = amount

    def _process_fee_update(self, msg):
        """Call this with a message like a server_info response. Will
        affect fee calculations."""
        i = self.fee_info
        # Result to a subscribe command will contain those
        i['load_base'] = msg.get('load_base', i['load_base'])
        i['load_factor'] = msg.get('load_factor', i['load_factor'])

        # Note: the ledger stream gives us data for fee_ref and fee_base.
        # The ripple client uses these to calculate the XRP value of a
        # fee unit, though the Wiki instructions to calculate fees do not
        # mention it. We'll ignore it for now.

    def request_account_info(self, account):
        return self.execute("account_info", account=account)['account_data']

    def submit(self, tx_blob=None, tx_json=None, secret=None):
        """Submit the transaction.

        You may either send a signed transaction (as a serialized
        tx_blob or unserialized dict, both as ``tx_blob``), or you
        may pass a secret and a ``tx_json`` dict to let the server
        do the signing.
        """
        assert not (tx_blob and tx_json)
        if isinstance(tx_blob, dict):
            tx_blob = serialize_object(tx_blob)

        return self.execute(
            "submit", tx_blob=tx_blob, tx_json=tx_json, secret=secret)

    def find_path_once(self, source, destination, destination_amount,
                       source_currencies=None):
        """Use the ``ripple_path_find`` API to find a path"""
        return self.execute(
            "ripple_path_find", source_account=source,
            destination_account=destination,
            destination_amount=destination_amount,
            source_currencies=source_currencies
        )

    def path_find(self):
        # Start an ongoing path-finding process. Uses the ``path_find``
        # API instead.
        raise NotImplementedError()


class DeferredTransaction(object):
    """The difference to DeferredResponse is that this one will
    always be resolved with an actual transaction result. However,
    the transaction may indicate a failure.
    """
    # TODO: Can we just re-use DeferredResponse? - at least extend it

    def __init__(self, tx, txhash):
        self.tx = tx
        self.hash = txhash
        self.resolved = threading.Event()
        self.result = self.error = None

    def wait(self, timeout=None):
        self.resolved.wait(timeout)
        if self.error:
            raise TransactionError(self.error, self.result)
        return self.result

    def resolve(self, result, error=None):
        self.result = result
        self.error = error
        self.resolved.set()


class Remote(object):
    """This is supposed to be a more high-level API that ideally
    will be able to manage multiple server connections, can track
    the state of submitted transactions etc.

    This is partially async. That is, it blocks while waiting for
    direct server responses, but is async for transaction handling,
    where the server cannot be expected to give a final response
    without significant delay.
    """

    def __init__(self, url, secret):
        self.secret = secret
        self._sequence_cache = {}
        self._pending_transactions = {}
        self._pending_transactions_lock = threading.RLock()

        # Connect to the client
        self.client = Client(url)
        # Start a subscription to transaction updates
        # TODO: Should we only do this once we begin sending payments?
        _, queue = self.client.subscribe(streams=['server', 'transactions'])

        # This thread will deal with subscription updates
        self.read_thread = threading.Thread(target=self._read_proc, args=(queue,))
        self.read_thread.setDaemon(True)
        self.read_thread.start()

    def _read_proc(self, queue):
        try:
            while not getattr(self, '_shutdown', False):
                try:
                    msg = queue.get(timeout=0.2)
                except Empty:
                    continue
                if msg['type'] == 'serverStatus':
                    # TODO: Thread: needs to lock!
                    self.client._process_fee_update(msg)

                if msg['type'] == 'transaction':
                    # See if this is a transaction that interests us
                    hash = msg['transaction']['hash']
                    with self._pending_transactions_lock:
                        if hash in self._pending_transactions:
                            # The JS client, when a transaction comes in,
                            # doesn't seem to check any field except
                            # validated, and then just considered the
                            # transaction a success, which I find a bit
                            # strange. But do likewise.
                            if not msg['validated']:
                                msg = RippleError(
                                    'received non-validated transaction, is '
                                    'this legit? %s' % msg)

                            self._pending_transactions[hash].resolve(msg)
                            del self._pending_transactions[hash]

        except Exception as e:
            # On error, notify all watches
            with self._pending_transactions_lock:
                for transaction in self._pending_transactions.values():
                    transaction.resolve(e)
            raise

        log.debug('remote.read_proc now shut down')

    def close(self):
        log.debug('remote.close()')
        self._shutdown = True
        self.client.close()

    def get_sequence_number(self, account):
        if not account in self._sequence_cache:
            # Will update the cache
            self.account_info(account)
        current = self._sequence_cache[account]
        self._sequence_cache[account] += 1
        return current

    def account_info(self, account):
        info = self.client.request_account_info(account)
        self._sequence_cache[account] = info['Sequence']
        return info

    def send_payment(self, destination, amount, account=None, flags=None,
            destination_tag=None):
        # Parse the amount
        amount = Amount(amount)

        # Determine the sender address
        if not account:
            if not self.secret:
                raise ValueError(
                    'If you do not provide a sender account, you need to '
                    'give a secret so one can be derived.')
            account = get_ripple_from_secret(self.secret)

        # If the amount to send does not include an issuer, setting it
        # to the destination address makes ripple pick one.
        if amount.currency != 'XRP':
            if not 'issuer' in amount:
                amount['issuer'] = destination

        # For non-xrp payments, we need to have a path
        if amount.currency == 'XRP':
            paths = None
        else:
            pfr = self.client.find_path_once(
                source=account, destination=destination,
                destination_amount=amount
            )
            if not pfr['alternatives']:
                raise ValueError('No path found for this payment')
            paths = pfr['alternatives'][0]['paths_computed']

        tx = {
            "TransactionType" : "Payment",
            "Account" : account,
            "Destination" : destination,
            "Amount" : amount
        }
        if destination_tag:
            tx['DestinationTag'] = destination_tag
        if flags is not None:
            tx['Flags'] = flags
        if paths is not None:
            tx['Paths'] = paths

        return self.submit(account, tx)

    def submit(self, account, tx_json):
        """Returns a DeferredTransaction that you should wait() on.

        Or, raises an exception immediately during client.submit().
        """
        # Add a fee
        self.client.add_fee(tx_json)

        # Add sequence number
        tx_json['Sequence'] = self.get_sequence_number(account)

        # Sign the transaction
        sign_transaction(tx_json, self.secret)
        txhash = transaction_hash(tx_json)

        # Prepare a deferred result value
        pending = DeferredTransaction(tx_json, txhash)

        # Now submit
        result = self.client.submit(tx_blob=tx_json)

        # Let's deal with the result
        # This is analog to how ripple-client deals with transactions.
        # Plus, see:
        #   https://ripple.com/wiki/Transaction_errors
        #   https://ripple.com/wiki/Robustly_submitting_a_transaction
        error_code = result['engine_result']
        error_cat = error_code[:3]

        if error_cat == 'tec':
            # Fee was claimed, but transaction did not succeed.
            # Wiki claims this may be a proposed disposition, but JS client
            # just goes to error and finalizes.
            pending.resolve(result, error=error_code)
        elif error_cat == 'tes':
            # Success - proposed disposition.
            # JS client will emit an unused proposed event and then will
            # simply watch the transaction stream to confirm.
            self._pending_transactions[txhash] = pending
        elif error_cat == 'tef':
            # 'Failure': JS client will error out the transaction, unless
            # the message is tefPAST_SEQ: then it will resubmit three
            # ledgers later with a locally adjusted sequence number to
            # account for transactions happened in the intermediary.
            # TODO:  We don't do resubmission for now.
            pending.resolve(result, error=error_code)
        elif error_cat == 'ter':
            # Did not succeed initially, but may still, according to Wiki.
            # Despite this, the JS client first explicitly fetches a new
            # sequence number from the server and then resubmits. This
            # sounds like a potential race condition leading to a double
            # spend to me.
            # TODO: Anyway, we don't do resubmission for now.
            pending.resolve(result, error=error_code)
        else:
            # Default - must be tem (malFormed) or tel (local); those are
            # final failures.
            # TODO: JS client resubmits on tooBusy one ledger later
            pending.resolve(result, error=error_code)
            self._sequence_cache[account] -= 1

        return pending
