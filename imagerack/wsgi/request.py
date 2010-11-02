"""
request.py
"""

import simplejson

class Request(object):
    """
    Create a "request" object out of an environ and start_response function.
    """

    def __init__(self, environ):
        """
        Parse environ and assign start_response)
        """
        self.environ = environ
        environ = environ.copy()

        self.path = environ["PATH_INFO"]
        self.method = environ["REQUEST_METHOD"]
        self.content_type = environ["CONTENT_TYPE"]

        if environ["QUERY_STRING"]:
            self.get = dict([part.split('=') for part in environ["QUERY_STRING"].split('&')])
        else:
            self.get = {}

        if environ["wsgi.input"].content_length:
            self.post = environ["wsgi.input"]

