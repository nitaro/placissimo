#!/usr/bin/python 3

""" This module contains a class that provides a RESTful API to the application state. """

# import modules.
import logging
from tornado import web


class StateHandler(web.RequestHandler):
    """ This class provides a RESTful API to the application state. """


    def initialize(self, get_endpoint_paths, task_metadata, thread_pool, websocket_connections, 
        allow_websocket, allow_get):
        """ Initializes the @web.RequestHandler subclass. 

        Args:
        - get_endpoint_paths (function): Returns available endpoint paths. Each item is a string.
        - task_metadata (dict): Keys are thread names, values are a dict with human-readable 
        metadata about tasks, whether finished or not.
        - thread_pool (concurrent.futures.ThreadPoolExecutor): The pool of task threads.
        - websocket_connections (list): All connected websocket clients. Each item is an instance of
        placissimo.lib.handlers.websocket_handler.WebsocketHandler. This will be None if websockets
        are not used.
        - allow_websocket (bool): Use True to enable the "/websocket" endpoint.
        - allow_get (bool): Use True to allow GET access. Otherwise, use False to restrict access to 
        POST-only requests.
        """

        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.get_endpoint_paths = get_endpoint_paths
        self.task_metadata = task_metadata
        self.thread_pool = thread_pool
        self.websocket_connections = websocket_connections
        self.allow_websocket = allow_websocket 
        self.allow_get = allow_get


    def _get_state(self):
        """ Creates metadata about the current application state. 
        
        Returns:
            dict: The return value.
        """
        
        # create dict for application state.
        logging.info("Checking application state.")
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
