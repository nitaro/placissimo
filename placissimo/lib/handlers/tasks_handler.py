#!/usr/bin/python 3

""" This module contains a class that provides a RESTful API to task metadata. """

# import modules.
import logging
from tornado import web


class TasksHandler(web.RequestHandler):
    """ This class provides a RESTful API to task metadata. """


    def initialize(self, task_metadata, allow_get):
        """ Initializes the @web.RequestHandler subclass. 

        Args:
            - task_metadata (dict): Keys are thread names, values are a dict with human-readable
            metadata about tasks, whether finished or not. 
            - allow_get (bool): Use True to allow GET access. Otherwise, use False to restrict 
            access to POST-only requests.
        """

        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.task_metadata = task_metadata
        self.allow_get = allow_get


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
