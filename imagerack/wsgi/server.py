"""
Logic/Code/Daemon for a Python WSGI server.
"""

from gevent import pywsgi
from daemonhelper import GeventDaemon, make_main
from imagerack.wsgi.handlers import WsgiHandler

class ImagerackDaemon(GeventDaemon):
    """
    ImagerackDaemon class! Yay!
    """

    name = "imagerack"

    def __init__(self):
        """
        Initialize the management daemon.
        """
        GeventDaemon.__init__(self)

        # WSGI configuration from daemon config
        host = self.config("wsgi-server", "host", "0.0.0.0", str)
        port = self.config("wsgi-server", "port", 80, int)
        debug = self.config("wsgi-server", "debug", True, bool)

        # Get reference to the database we're using
        base = self.config("storage", "base", "/srv/imagerack", str)
        self.img_path = "%s/%s" % (base, self.config("storage", "img", "images", str))
        self.web_path = "%s/%s" % (base,  self.config("storage", "web", "web", str))

        # Create WSGI server
        self.server = pywsgi.WSGIServer((host, port))
        self.server.application = WsgiHandler(self.logger, self.img_path, self.web_path)

    def handle_run(self):
        """
        Logic for starting the DMS management daemon.
        """
        self.server.serve_forever()

    def handle_stop(self):
        """
        Logic for stopping the DMS management daemon.
        """
        self.server.stop()

main = make_main(ImagerackDaemon)
