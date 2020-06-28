#!/usr/bin/python3

""" This module contains a class that serves up a specified HTML file. """

# import modules.
from .base_handler import BaseHandler
from tornado import web


class IndexHandler(BaseHandler):
    """ This class serves up a specified HTML file. """

    def initialize(self, **server_locals):

        super().initialize(__name__, **server_locals)

    def _render_file(self):
        """ Renders @self.index_file. """

        self.logger.info("Rendering HTML file: {}".format(self.index_file))

        try:
            self.render(self.index_file, render_object=self.render_object,
                        server_locals=self.server_locals)
        except Exception as err:
            self.logger.warning(
                "Can't render file: {}".format(self.index_file))
            self.logger.error(err)

        return

    @web.asynchronous
    def get(self):
        """ Implements GET requests. 

        Returns:
            None
        """

        self._render_file()
        return

    @web.asynchronous
    def post(self):
        """ Implements POST requests. 

        Returns:
            None
        """

        self._render_file()
        return


if __name__ == "__main__":
    pass
