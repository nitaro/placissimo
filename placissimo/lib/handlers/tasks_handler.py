#!/usr/bin/python3

""" This module contains a class that provides a RESTful API to task metadata. 

Todo:
    * Consolidate redundant logic in GET/POST.
    * Add start/limit params.
"""

# import modules.
from .base_handler import BaseHandler
from tornado import web


class TasksHandler(BaseHandler):
    """ This class provides a RESTful API to task metadata. """

    def initialize(self, **server_locals):

        super().initialize(__name__, **server_locals)

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

        # get the task's thread name.
        thread_name = self.get_query_argument("name", default=None)

        # extract the appropriate metadata from @self.task_metadata.
        if thread_name is None:
            tasks = self.task_metadata
        elif thread_name in self.task_metadata:
            tasks = {thread_name: self.task_metadata[thread_name]}
        else:
            self.logger.warning("Task identifier doesn't exist.")
            tasks = {}

        # send metadata.
        self.write(tasks)
        self.finish()

        return

    @web.asynchronous
    def post(self):
        """ Implements POST requests. 

        Returns:
            None
        """

        # get the task's thread name.
        thread_name = self.get_argument("name", default=None)

        # extract the appropriate metadata from @self.task_metadata.
        if thread_name is None:
            tasks = self.task_metadata
        elif thread_name in self.task_metadata:
            tasks = {thread_name: self.task_metadata[thread_name]}
        else:
            self.logger.warning("Task identifier doesn't exist.")
            tasks = {}

        # send metadata.
        self.write(tasks)
        self.finish()

        return


if __name__ == "__main__":
    pass
