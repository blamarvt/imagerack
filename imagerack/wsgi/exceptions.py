"""
exceptions.py
"""

import httplib
import simplejson

class WsgiException(Exception):
    """
    Generic WSGI exception class which serves as a base class.
    """

    code = httplib.INTERNAL_SERVER_ERROR

    def __init__(self, request, message=None):
        """
        Take a request for subclasses to utilize
        """
        self.content = message or "%d %s" % (self.code, httplib.responses[self.code])
        self.request = request
        self.headers = []

    def __repr__(self):
        """
        East to read representation of the exception.
        """
        return "<%s status=%s>" % (self.__class__.__name__, self.get_status())

    def get_status(self):
        """
        Return useful status information (e.g. 404 Not Found)
        """
        return "%d %s" % (self.code, httplib.responses[self.code])


class JsonContent(WsgiException):
    """
    200 OK w/ JSON content
    """

    code = httplib.OK

    def __init__(self, request, content = None):
        """
        Encode and return the content with JSON headers
        """
        WsgiException.__init__(self, request)
        self.content = simplejson.dumps(content)
        self.headers = [('Content-Type', 'application/json')]

class Redirect(WsgiException):
    """
    303 See Other
    """
    
    code = httplib.SEE_OTHER

    def __init__(self, request, location):
        """
        Redirect
        """
        WsgiException.__init__(self, request)
        self.location = location
        self.headers = [("Location", self.location)]


class Content(WsgiException):
    """
    200 OK w/ JSON content
    """

    code = httplib.OK

    def __init__(self, request, content = None):
        """
        Encode and return the content with JSON headers
        """
        WsgiException.__init__(self, request)
        self.content = content
        self.headers = [('Content-Type', 'application/json')]


class NoContent(WsgiException):
    """
    204 No Content
    """

    code = httplib.NO_CONTENT


class NotFound(WsgiException):
    """
    404 Not Found response
    """

    code = httplib.NOT_FOUND


class NotImplemented(WsgiException):
    """
    501 Not Implemented response
    """

    code = httplib.NOT_IMPLEMENTED


class BadRequest(WsgiException):
    """
    400 Bad Request
    """

    code = httplib.BAD_REQUEST


class Forbidden(WsgiException):
    """
    403 Forbidden
    """

    code = httplib.FORBIDDEN


class StaticContent(WsgiException):
    """
    Static file
    """

    content_type = None
    last_modified = None
    date_format = "%a, %d %b %Y %H:%M:%S GMT"

    def __init__(self, request, path):
        """
        Populate content with path data
        """
        import os
        import time
        import mimetypes

        if not os.path.exists(path):
            raise NotFound(request)

        if not os.access(path, os.R_OK):
            raise Forbidden(request)

        self.content_type = mimetypes.guess_type(path)[0]
        last_modified = time.gmtime(os.stat(path).st_mtime)
        self.last_modified = time.strftime(self.date_format, last_modified)

        self.code = httplib.OK
        self.headers = [
            ('Content-Type', self.content_type),
            ('Last-Modified', self.last_modified)
        ]
        self.content = open(path)
