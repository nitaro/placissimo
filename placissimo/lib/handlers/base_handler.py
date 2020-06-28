#!/usr/bin/python3

""" This module contains a generic tornado.web.RequestHandler class. """

# import modules.
import logging
from tornado import web


class BaseHandler(web.RequestHandler):
    """ This class is a generic tornado.web.RequestHandler.

    Args:
        - server_locals (dict): The public attributes of placissimo.server.
    """

    def initialize(self, name, **server_locals):

        # set logging.
        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.server_locals = server_locals
        for k, v in server_locals.items():
            setattr(self, k, v)

        # allow CORS per: https://stackoverflow.com/a/40431557
        self.set_header("Access-Control-Allow-Origin", "*")


if __name__ == "__main__":
    pass
