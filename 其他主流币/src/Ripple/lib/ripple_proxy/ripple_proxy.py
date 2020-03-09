import json
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError


class RippleProxy(object):
    def __init__(self, node: str = 'https://data.ripple.com'):
        self.node = node

    def __repr__(self):
        return '<RippleDataAPIClient node=%r>' % self.node

    # def _call(self, url_params: tuple, params: dict) -> dict:
    #     """
    #     Send request to data API
    #     :param url_params: url parameters which are forming endpoint
    #     :param params: query params
    #     :return: response dict
    #     """
    #     api_version = "/v2/"
    #     endpoint = "/".join(url_params)
    #     api_url = "".join((api_version, endpoint))
    #     url = urljoin(self.node, api_url)
    #     data = json.dumps(params).encode('utf-8')
    #     req = Request(method='GET', url=url, data=data)
    #     try:
    #         with urlopen(req) as res:
    #             res_json = json.loads(res.fp.read().decode('utf-8'))
    #             return res_json
    #     except HTTPError as err:
    #         return {"status": "error", "msg": err}
    #     except URLError as err:
    #         return {"status": "error", "msg": err}

    def _call(self, url_params: tuple, params: dict) -> dict:
        """
        Send request to data API
        :param url_params: url parameters which are forming endpoint
        :param params: query params
        :return: response dict
        """
        api_version = "/v2/"
        endpoint = "/".join(url_params)
        api_url = "".join((api_version, endpoint))
        url = urljoin(self.node, api_url)
        # data = json.dumps(params).encode('utf-8')
        options = urlencode(params)
        url_full = url + "?" + options
        # req = Request(method='GET', url=url, data=data)
        req = Request(method='GET', url=url_full)
        try:
            with urlopen(req) as res:
                res_json = json.loads(res.fp.read().decode('utf-8'))
                return res_json
        except HTTPError as err:
            return {"status": "error", "msg": err}
        except URLError as err:
            return {"status": "error", "msg": err}

    def get_ledger(self, ledger_identifier: str, **query_params) -> dict:
        """
        Retrieve a specific Ledger by hash, index, date, or latest validated.
        Reference: https://developers.ripple.com/data-api.html#get-ledger
        """
        url_params = 'ledgers', ledger_identifier
        return self._call(url_params, query_params)

    def get_ledger_validations(self, ledger_hash: str, **query_params) -> dict:
        """
        Retrieve a any validations recorded for a specific ledger hash. This dataset includes ledger versions
        that are outside the validated ledger chain.
        Reference: https://developers.ripple.com/data-api.html#get-ledger-validations
        """
        endpoint = 'ledgers', ledger_hash, 'validations'
        return self._call(endpoint, query_params)

    def get_ledger_validation(self, ledger_hash: str,
                              pubkey: str, **query_params) -> dict:
        """
        Retrieve a validation vote recorded for a specific ledger hash by a specific validator.
        This dataset includes ledger versions that are outside the validated ledger chain
        Reference: https://developers.ripple.com/data-api.html#get-ledger-validation
        """
        url_params = 'ledgers', ledger_hash, 'validations', pubkey
        return self._call(url_params, query_params)

    def get_transaction(self, hash: str, **query_params) -> dict:
        """
        Retrieve a specific transaction by its identifying hash.
        Reference: https://developers.ripple.com/data-api.html#get-transaction
        """
        url_params = 'transactions', hash
        return self._call(url_params, query_params)

    def get_transactions(self, **query_params) -> dict:
        """
        Retrieve transactions by time
        Reference: https://developers.ripple.com/data-api.html#get-transactions
        """
        return self._call(('transactions', ), query_params)

    def get_payments(self, currency: str = None, **query_params) -> dict:
        """
        Retrieve Payments over time, where Payments are defined as Payment type transactions where the sender
        of the transaction is not also the destination.
        Reference: https://developers.ripple.com/data-api.html#get-payments
        """
        url_params = 'payments'
        if currency:
            url_params = 'payments', currency
        return self._call(url_params, query_params)

    def get_exchanges(self, base: str, counter: str, **query_params) -> dict:
        """
        Retrieve Exchanges for a given currency pair over time. Results can be returned as individual exchanges
        or aggregated to a specific list of intervals
        Reference: https://developers.ripple.com/data-api.html#get-exchanges
        """
        url_params = 'exchanges', base, counter
        return self._call(url_params, query_params)

    def get_exchange_rates(self, base: str, counter: str,
                           **query_params) -> dict:
        """
        Retrieve an exchange rate for a given currency pair at a specific time.
        Reference: https://developers.ripple.com/data-api.html#get-exchange-rates
        """
        url_params = 'exchange_rates', base, counter
        return self._call(url_params, query_params)

    def normalize(self, **query_params) -> dict:
        """
        Convert an amount from one currency and issuer to another, using the network exchange rates.
        Reference: https://developers.ripple.com/data-api.html#normalize
        """
        return self._call(('normalize', ), query_params)

    def get_daily_reports(self, date: str = None, **query_params) -> dict:
        """
        Retrieve per account per day aggregated payment summaries
        Refernce: https://developers.ripple.com/data-api.html#get-daily-reports
        """
        url_params = 'reports'
        if date:
            url_params = 'reports', date
        return self._call(url_params, query_params)

    def get_stats(self, **query_params) -> dict:
        """
        Retrieve statistics about transaction activity in the XRP Ledger, divided into intervals of time.
        Reference: https://developers.ripple.com/data-api.html#get-stats
        """
        return self._call(('stats', ), query_params)

    def get_active_accounts(self, base: str, counter: str,
                            **query_params) -> dict:
        """
        Get information on which accounts are actively trading in a specific currency pair.
        Reference: https://developers.ripple.com/data-api.html#get-active-accounts
        """
        url_params = 'active_accounts', base, counter
        return self._call(url_params, query_params)

    def get_exchange_volume(self, **query_params) -> dict:
        """
        Get aggregated exchange volume for a given time period.
        The API returns results in units of a single display currency rather than many different currencies.
        The conversion uses standard rates to and from XRP.
        Reference: https://developers.ripple.com/data-api.html#get-exchange-volume
        """
        url_params = 'network', 'exchange_volume'
        return self._call(url_params, query_params)

    def get_payment_volume(self, **query_params) -> dict:
        """
        Get aggregated payment volume for a given time period.
        The API returns results in units of a single display currency rather than many different currencies.
        The conversion uses standard rates to and from XRP.
        Reference: https://developers.ripple.com/data-api.html#get-payment-volume
        """
        url_params = 'network', 'payment_volume'
        return self._call(url_params, query_params)

    def get_external_markets(self, **query_params) -> dict:
        """
        Get aggregated exchange volume from a list of off ledger exchanges for a specified rolling interval.
        The API returns results in units of a single display currency rather than many different currencies.
        The conversion uses standard rates to and from XRP.
        Reference: https://developers.ripple.com/data-api.html#get-external-markets
        """
        url_params = 'network', 'external_markets'
        return self._call(url_params, query_params)

    def get_xrp_distribution(self, **query_params) -> dict:
        """
        Get information on the total amount of XRP in existence and in circulation, by weekly intervals.
        The API returns results in units of a single display currency rather than many different currencies.
        The conversion uses standard rates to and from XRP.
        Reference: https://developers.ripple.com/data-api.html#get-xrp-distribution
        """
        url_params = 'network', 'xrp_distribution'
        return self._call(url_params, query_params)

    def get_top_currencies(self, date: str = None, **query_params) -> dict:
        """
        Returns the top currencies on the XRP Ledger, ordered from highest rank to lowest.
        Reference: https://developers.ripple.com/data-api.html#get-top-currencies
        """
        url_params = 'network', 'top_currencies'
        if date:
            url_params = 'network', 'top_currencies', date
        return self._call(url_params, query_params)

    def get_top_markets(self, date: str = None, **query_params) -> dict:
        """
        Returns the top exchange markets on the XRP Ledger, ordered from highest rank to lowest.
        Reference: https://developers.ripple.com/data-api.html#get-top-markets
        """
        url_params = 'network', 'top_markets'
        if date:
            url_params = 'network', 'top_markets', date
        return self._call(url_params, query_params)

    def get_transaction_costs(self, **query_params) -> dict:
        """
        Returns transaction cost stats per ledger, hour, or day. The data shows the average, minimum, maximum,
        and total transaction costs paid for the given interval or ledger.
        Reference: https://developers.ripple.com/data-api.html#get-transaction-costs
        """
        url_params = 'network', 'fees'
        return self._call(url_params, query_params)

    def get_fee_stats(self, **query_params) -> dict:
        """
        Returns snapshots of the metrics derived from rippled's fee command.
        Reference: https://developers.ripple.com/data-api.html#get-fee-stats
        """
        url_params = 'network', 'fee_stats'
        return self._call(url_params, query_params)

    def get_topology(self, **query_params) -> dict:
        """
        Get known rippled servers and peer-to-peer connections between them.
        Reference: https://developers.ripple.com/data-api.html#get-topology
        """
        url_params = 'network', 'topology'
        return self._call(url_params, query_params)

    def get_topology_nodes(self, **query_params) -> dict:
        """
        Get known rippled nodes. (This is a subset of the data returned by the Get Topology method.)
        Reference: https://developers.ripple.com/data-api.html#get-topology-nodes
        """
        url_params = 'network', 'topology', 'nodes'
        return self._call(url_params, query_params)

    def get_topology_node(self, pubkey: str, **query_params) -> dict:
        """
        Get information about a single rippled server by its node public key (not validator public key).
        Reference: https://developers.ripple.com/data-api.html#get-topology-node
        """
        url_params = 'network', 'topology', 'nodes', pubkey
        return self._call(url_params, query_params)

    def get_topology_links(self, **query_params) -> dict:
        """
        Get information on peer-to-peer connections between rippled servers.
        (This is a subset of the data returned by the Get Topology method.)
        Reference: https://developers.ripple.com/data-api.html#get-topology-links
        """
        url_params = 'network', 'topology', 'links'
        return self._call(url_params, query_params)

    def get_validator(self, pubkey: str, **query_params) -> dict:
        """
        Get details of a single validator in the consensus network.
        Reference: https://developers.ripple.com/data-api.html#get-validator
        """
        url_params = 'network', 'validators', pubkey
        return self._call(url_params, query_params)

    def get_validators(self, **query_params) -> dict:
        """
        Get a list of known validators.
        Reference: https://developers.ripple.com/data-api.html#get-validators
        """
        url_params = 'network', 'validators'
        return self._call(url_params, query_params)

    def get_validator_validations(self, pubkey: str, **query_params) -> dict:
        """
        Retrieve validation votes signed by a specified validator, including votes for ledger
        versions that are outside the main ledger chain
        Reference: https://developers.ripple.com/data-api.html#get-validator-validations
        """
        url_params = 'network', 'validators', pubkey, 'validations'
        return self._call(url_params, query_params)

    def get_validations(self, **query_params) -> dict:
        """
        Retrieve validation votes, including votes for ledger versions that are outside the main ledger chain.
        Reference: https://developers.ripple.com/data-api.html#get-validations
        """
        url_params = 'network', 'validations'
        return self._call(url_params, query_params)

    def get_single_validator_reports(
            self, pubkey: str, **query_params) -> dict:
        """
        Get a single validator's validation vote stats for 24-hour intervals.
        Reference: https://developers.ripple.com/data-api.html#get-single-validator-reports
        """
        url_params = 'network', 'validators', pubkey, 'reports'
        return self._call(url_params, query_params)

    def get_daily_validator_reports(self, **query_params) -> dict:
        """
        Get a validation vote stats and validator information for all known validators in a 24-hour period.
        Reference: https://developers.ripple.com/data-api.html#get-daily-validator-reports
        """
        url_params = 'network', 'validator_reports'
        return self._call(url_params, query_params)

    def get_rippled_versions(self, **query_params) -> dict:
        """
        Reports the latest versions of rippled available from the official Ripple Yum repositories.
        Reference: https://developers.ripple.com/data-api.html#get-rippled-versions
        """
        url_params = 'network', 'rippled_versions'
        return self._call(url_params, query_params)

    def get_all_gateways(self, **query_params) -> dict:
        """
        Get information about known gateways.
        Reference: https://developers.ripple.com/data-api.html#get-all-gateways
        """
        return self._call(('gateways', ), query_params)

    def get_gateway(self, gateway: str, **query_params) -> dict:
        """
        Get information about a specific gateway from the Data API's list of known gateways.
        Reference: https://developers.ripple.com/data-api.html#get-gateway
        """
        url_params = 'gateways', gateway
        return self._call(url_params, query_params)

    def get_currency_image(self, currencyimage: str, **query_params) -> dict:
        """
        Retrieve vector icons for various currencies.
        Reference: https://developers.ripple.com/data-api.html#get-currency-image
        """
        url_params = 'currencies', currencyimage
        return self._call(url_params, query_params)

    def get_accounts(self, **query_params) -> dict:
        """
        Retrieve information about the creation of new accounts in the XRP Ledger.
        Reference: https://developers.ripple.com/data-api.html#get-accounts
        """
        return self._call(('accounts', ), query_params)

    def get_account(self, address: str, **query_params) -> dict:
        """
        Get creation info for a specific ripple account
        Reference: https://developers.ripple.com/data-api.html#get-account
        """
        url_params = 'accounts', address
        return self._call(url_params, query_params)

    def get_account_balances(self, address: str, **query_params) -> dict:
        """
        Get all balances held or owed by a specific XRP Ledger account.
        Reference: https://developers.ripple.com/data-api.html#get-account-balances
        """
        url_params = 'accounts', address, 'balances'
        return self._call(url_params, query_params)

    def get_account_orders(self, address: str, **query_params) -> dict:
        """
        Get orders in the order books, placed by a specific account. This does not return orders that have
        already been filled.
        Reference: https://developers.ripple.com/data-api.html#get-account-orders
        """
        url_params = 'accounts', address, 'orders'
        return self._call(url_params, query_params)

    def get_account_transaction_history(
            self, address: str, **query_params) -> dict:
        """
        Retrieve a history of transactions that affected a specific account.
        This includes all transactions the account sent, payments the account received,
        and payments that rippled through the account.
        Reference: https://developers.ripple.com/data-api.html#get-account-transaction-history
        """
        url_params = 'accounts', address, 'transactions'
        return self._call(url_params, query_params)

    def get_transaction_by_account_and_sequence(
            self, address: str, sequence: str, **query_params) -> dict:
        """
        Retrieve a specifc transaction originating from a specified account
        Reference: https://developers.ripple.com/data-api.html#get-transaction-by-account-and-sequence
        """
        url_params = 'accounts', address, 'transactions', sequence
        return self._call(url_params, query_params)

    def get_account_payments(self, address: str, **query_params) -> dict:
        """
        Retrieve a payments for a specified account
        Reference: https://developers.ripple.com/data-api.html#get-account-payments
        """
        url_params = 'accounts', address, 'payments'
        return self._call(url_params, query_params)

    def get_account_exchanges(
            self, address: str, base: str = None, counter: str = None, **
            query_params) ->dict:
        """
        Retrieve Exchanges for a given account over time.
        Reference: https://developers.ripple.com/data-api.html#get-account-exchanges
        """
        url_params = 'accounts', address, 'exchanges'
        if base and counter:
            url_params = 'accounts', address, 'exchanges', base, counter
        return self._call(url_params, query_params)

    def get_account_balance_changes(
            self, address: str, **query_params) -> dict:
        """
        Retrieve Balance changes for a given account over time.
        Reference: https://developers.ripple.com/data-api.html#get-account-balance-changes
        """
        url_params = 'accounts', address, 'balance_changes'
        return self._call(url_params, query_params)

    def get_account_reports(
            self, address: str, date: str = None, **query_params) -> dict:
        """
        Retrieve daily summaries of payment activity for an account.
        Reference: https://developers.ripple.com/data-api.html#get-account-reports
        """
        url_params = 'accounts', address, 'reports'
        if date:
            url_params = 'accounts', address, 'reports', date
        return self._call(url_params, query_params)

    def get_account_transaction_stats(
            self, address: str, **query_params) -> dict:
        """
        Retrieve daily summaries of transaction activity for an account.
        Reference: https://developers.ripple.com/data-api.html#get-account-transaction-stats
        """
        url_params = 'accounts', address, 'stats', 'transactions'
        return self._call(url_params, query_params)

    def get_account_value_stats(self, address: str, **query_params) -> dict:
        """
        Retrieve daily summaries of transaction activity for an account.
        Reference: https://developers.ripple.com/data-api.html#get-account-value-stats
        """
        url_params = 'accounts', address, 'stats', 'value'
        return self._call(url_params, query_params)

    def check_api(self, **query_params) -> dict:
        """
        Check the health of the API service.
        Reference: https://developers.ripple.com/data-api.html#health-check-api
        """
        url_params = 'health', 'api'
        return self._call(url_params, query_params)

    def check_ledger_importer(self, **query_params) -> dict:
        """
        Check the health of the Ledger Importer Service.
        Reference: https://developers.ripple.com/data-api.html#health-check-ledger-importer
        """
        url_params = 'health', 'importer'
        return self._call(url_params, query_params)

    def check_nodes_etl(self, **query_params) -> dict:
        """
        Check the health of the Topology Nodes Extract, Transform, Load (ETL) Service.
        Reference: https://developers.ripple.com/data-api.html#health-check-nodes-etl
        """
        url_params = 'health', 'nodes_etl'
        return self._call(url_params, query_params)

    def check_validations_etl(self, **query_params) -> dict:
        """
        Check the health of the Validations Extract, Transform, Load (ETL) Service.
        Reference: https://developers.ripple.com/data-api.html#health-check-validations-etl
        """
        url_params = 'health', 'validations_etl'
        return self._call(url_params, query_params)
