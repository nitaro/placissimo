#!/usr/bin/python3

""" This module contains a class that provides a RESTful API to the application state. """

# import modules.
import json
from .base_handler import BaseHandler
from tornado import web


class StateHandler(BaseHandler):
    """ This class provides a RESTful API to the application state. """

    def initialize(self, **server_locals):

        super().initialize(__name__, **server_locals)

    def _get_state(self):
        """ Creates metadata about the current application state. 

        Returns:
            dict: The return value.
        """

        # create dict for application state.
        self.logger.info("Checking application state.")
        running_threads = sum([1 for t in self.task_metadata
                               if not self.task_metadata[t].get("done")])
        state = {"endpoints": self.get_endpoint_paths(),
                 "running_threads": running_threads,
                 "available_threads": self.thread_pool._max_workers - running_threads,
                 "websocket_connections": len(self.websocket_connections)
                 if self.allow_websocket else None}

        return state

    @web.asynchronous
    def get(self):
        """ Implements GET requests. If @self.allow_get is False, sends a 403.

        Returns:
            None
        """

        # if GET access is restricted, return an error.
        if not self.allow_get:
            self.logger.warning("GET requests are forbidden.")
            self.send_error(403)
            return

        # send application state.
        self.write(self._get_state())
        self.finish()

        return

    @web.asynchronous
    def post(self):
        """ Implements POST requests. 

        Returns:
            None
        """

        # send application state.
        self.write(self._get_state())
        self.finish()

        return


if __name__ == "__main__":
    pass
