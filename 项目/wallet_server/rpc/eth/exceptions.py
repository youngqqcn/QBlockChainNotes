
class JsonRpcError(IOError):#Exception):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        super(JsonRpcError, self).__init__(*args, **kwargs)



class BadConnectionError(JsonRpcError):

    pass


class BadStatusCodeError(JsonRpcError):
    pass


class BadJsonError(JsonRpcError):
    pass


class BadResponseError(JsonRpcError):
    pass
