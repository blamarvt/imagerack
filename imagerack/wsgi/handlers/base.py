"""
Initialize all things WSGI Handlers
"""

import re
import os

from PIL import Image
from StringIO import StringIO
from pprint import pformat
from collections import defaultdict
from imagerack.wsgi.request import Request
from imagerack.wsgi.exceptions import WsgiException, NotImplemented, \
    NotFound, NoContent, Content, JsonContent, BadRequest, StaticContent, Redirect

class WsgiHandler(object):
    """
    WsgiHandler class! Yay?
    """

    routes = defaultdict(dict)

    def __init__(self, logger, img_path, web_path):
        """
        ???
        """
        self.logger = logger
        self.img_path = img_path
        self.web_path = web_path

    def __call__(self, environ, start_response):
        """
        ???
        """
        request = Request(environ)
        method = request.method
        routes = self.routes.get(method)

        try:
            if routes is None:
                raise NotImplemented(request)

            for func, exp in self.routes[method].items():
                match = re.match("^%s$" % exp, request.path)
                if match:
                    kwargs = match.groupdict()
                    raise func(self, request, **kwargs)

            raise NotFound(request)
    
        except WsgiException as e:
            start_response(e.get_status(), e.headers)
            return e.content

        except Exception as e:
            import traceback
            start_response("500 Internal Server Error", [])
            self.logger.error(traceback.format_exc())
            return "There was an error. Please email 'brian.lamar@rackspace.com'"

    def handle_post(self, request):
        """
        Attempt to insert a new image!
        """
        import base64, random
        from cgi import FieldStorage
        from tempfile import NamedTemporaryFile

        p = FieldStorage(fp=request.environ["wsgi.input"], environ=request.environ)

        tmp_image = NamedTemporaryFile()
        tmp_image.write(p.getvalue("image"))
        tmp_image.flush()

        # Attempt to open
        try:
            image = Image.open(tmp_image.name)
        except IOError:
            raise Redirect(request, location="/?error=UnknownType")

        image.thumbnail((1280,1280))
        counter = 0

        while True:
            name = base64.urlsafe_b64encode(str(random.randint(0, 65536)))
            path = "%s/%s.jpg" % (self.img_path, name)

            if not os.path.exists(path):
                break
            else:
                counter += 1

            if counter > 10:
                raise Redirect(request, location="/?error=OutOfNumbers")

        try:
            image.save(path)
            self.logger.info("Saved image %s" % name)
        except Exception:
            raise Redirect(request, location="/?error=ProbablySomethingBad")

        raise Redirect(request, location=name)

    def handle_image(self, request, name):
        """
        Show an image...
        """
        self.logger.info("Image request for %s" % name)
        return self.handle_static(request, "%s.jpg" % name, self.img_path)

    def handle_static(self, request, static_path, static_root = None):
        """
        Serves static files...not very well...
        """
        root = static_root or self.web_path
        path = os.path.normpath("%s/%s" % (root, static_path))
        if not path.startswith(root) or not re.match(r"[a-zA-Z0-9-/.]{1,1024}", static_path):
            raise BadRequest(request)

        raise StaticContent(request, path)

    def handle_index(self, request):
        """
        Serve the index...
        """
        self.logger.info("Homepage hit!")
        return self.handle_static(request, "index.html")

    routes["GET"][handle_index]  = r"/"
    routes["GET"][handle_static] = r"/static/(?P<static_path>.*)"
    routes["GET"][handle_image]  = r"/(?P<name>[\w=]{4,128})"
    routes["POST"][handle_post]  = r"/upload"
    
