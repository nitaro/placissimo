#!/usr/bin/python 3

""" This module contains a class that serves up a specified HTML file. """

# import modules.
import logging
from tornado import web


class IndexHandler(web.RequestHandler):
    """ This class serves up a specified HTML file. """


    def initialize(self, index_file, render_object, server_locals):
        """ Initializes the @web.RequestHandler subclass.

        Args:
            - index_file (str): The path to the HTML file to render at the "/" endpoint. The HTML
            file supports templating per: https://www.tornadoweb.org/en/stable/template.html.
            - render_object (object): Any object to pass to the rendered HTML file.
            - server_locals (dict): The non-private local vars for placissimo.server.serve().
        """
        
        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        
        # set attributes.
        self.index_file = index_file
        self.render_object = render_object
        self.server_locals = server_locals

    
    def _render_file(self):
        """ Renders @self.index_file. """

        self.logger.info("Rendering HTML file: {}".format(self.index_file))

        try:
            self.render(self.index_file, render_object=self.render_object, 
                server_locals=self.server_locals)
        except Exception as err:
            self.logger.warning("Can't render file: {}".format(self.index_file))
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