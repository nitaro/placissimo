#!/usr/bin/python 3

""" This module contains a function that handles all server endpoints. """

# import modules.
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from tornado import web, ioloop
from ..lib import dependency_error
from ..lib import log_manager
from .handlers.api_handler import ApiHandler
from .handlers.filesystem_handler import FilesystemHandler
from .handlers.index_handler import IndexHandler
from .handlers.state_handler import StateHandler
from .handlers.tasks_handler import TasksHandler
from .handlers.websocket_handler import WebsocketHandler


def serve(funk, server_name="servissimo", render_object=None, callback_arg=None, max_threads=None, 
    socket_filters=None, port=8080, index_file=None, filesystem_path=None, allow_websocket=False, 
    allow_broadcasts=False, allow_get=False, *args, **kwargs):
    """ Serves @funk at localhost:@port with the following endpoints:
            
            - "/": Provides a rendering of @index_file if it's not None.
            - "/api": Provides an interface to @funk.
            - "/state": Provides metadata about the current application state.
            - "/tasks": Provides task metadata.
            - "/filesystem": Provides file/folder listings starting at @filesystem_path if it's not
            None.
            - "/websocket": Provides a websocket interface to send and receive logging statements if
            @allow_websocket is True.
    
    Args:
        - funk (function): The user function.
        - server_name (str): The string that serves as the command line trigger to launch the 
        server. This value is also the prefix for the HTTP server's thread names. Use only letters.
        - render_object (object): Any object to pass to the rendered HTML file.
        - callback_arg (str): The name of the argument for @funk to which to pass back
        placissimo.server.serve()'s non-private local vars. Use None to omit passing anything back 
        to @funk.
        - max_threads (int): The number of concurrent threads to support. If None, the value will be
        based on your CPU per: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor.
        - socket_filters (list): Logging filters to add to the websocket logger. Each item in the 
        list must be an instance of logging.Filter. Use None if no filters are needed.
        - port (int): The port to use.
        - index_file (str): The path to the HTML file to render at the "/" endpoint. The HTML file
        supports templating per: https://www.tornadoweb.org/en/stable/template.html.
        - filesystem_path (str): The top-most directory for the "/filesystem" endpoint.
        - allow_websocket (bool): Use True to enable the "/websocket" endpoint. This requires that
        @index_file is not None.
        - allow_broadcasts (bool): Use True to allow messages sent by a given websocket client
        to be broadcast to all other connected clients.
        - allow_get (bool): Use True to allow GET access. Otherwise, use False to restrict access to 
        POST-only requests.

    Returns:
        None

    Raises:
        - TypeError: If @funk is not callable, if @max_threads is not an int, if @socket_filters is 
        not a list, if @port is not an int.
        - ValueError: If @server_name contains non-letters or if @port is not between 5000 and 9999.
        - FileNotFoundError: If @index_file is not a file.
        - dependency_error.DependencyError: If @allow_websocket is True and @index_file is None.
        - NotADirectoryError: If @filesystem_path is not a directory.
    """

    # set logging.
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    log_manager.handle_streams()

    # make sure @funk is a function.
    if not callable(funk):
        msg = "The type of @funk must be a function, not '{}'.".format(
            funk.__class__.__name__)
        logger.error(msg)
        raise TypeError(msg)

    # make sure @server_name contains only letters.
    if not server_name.isalpha():
        msg = "The @server_name '{}' contains non-letter characters.".format(server_name)
        logger.error(msg)
        raise ValueError(msg)
    
    # make sure @max_threads is None or an int.
    if max_threads is not None and not isinstance(max_threads, int):
        msg = "The type of @max_threads must be None or an integer, not '{}'.".format(
            max_threads.__class__.__name__)
        logger.error(msg)
        raise TypeError(msg)

    # make sure @socket_filters is a list.
    if socket_filters is not None and not isinstance(socket_filters, list):
        msg = "The type of @socket_filters must be a list, not '{}'.".format(
            socket_filters.__class__.__name__)
        logger.error(msg)
        raise TypeError(msg)
    
    # validate @port.
    if not isinstance(port, int):
        msg = "The port value must be an integer not: {}".format(type(port))
        raise TypeError(msg)
    if port < 5000 or port > 9999:
        msg = "The port value must be an integer between 5000 and 9999."
        raise ValueError(msg)
    
    # if needed, make sure @index_file exists.
    if index_file is not None:
        index_file = os.path.abspath(index_file)
        if not os.path.isfile(index_file):
            msg = "Can't find HTML file: {}".format(index_file)
            raise FileNotFoundError(msg)

    # if websockets are requested, make sure @index_file is not None.
    if allow_websocket and index_file is None:
        msg = "The \"/\" endpoint must be enabled if websockets are requested."
        raise dependency_error.DependencyError(msg)
            
    # if needed, make sure @filesystem_path exists.
    if filesystem_path is not None:
        filesystem_path = os.path.abspath(filesystem_path)
        if not os.path.isdir(filesystem_path):
            msg = "Can't find directory: {}".format(filesystem_path)
            raise NotADirectoryError(msg)

    # set parameters to pass to other modules.
    thread_prefix = "{}_".format(server_name)
    task_metadata = {}
    futures_metadata = {}
    thread_pool = ThreadPoolExecutor(max_workers=max_threads)
    websocket_connections = list() if allow_websocket else None

    # update the root logger so that websocket connections can emit logging messages.
    log_manager.handle_sockets(websocket_connections, allow_broadcasts, socket_filters)

    # prepaare endpoints.
    _endpoint_list = []
    get_endpoint_paths = lambda: [e[0] for e in sorted(_endpoint_list)]

    # get non-private locals().
    server_locals = {k:v for k,v in locals().items() if not k.startswith("_")}
    logging.debug("Logging @server_locals as '* {KEY}:{VALUE}' ...")
    for k, v in server_locals.items():
        logging.debug("* {} : {}".format(k, v))

    # set endpoints.
    _endpoint_list += [
        (r"/api", ApiHandler, dict(funk=funk, callback_arg=callback_arg, 
            server_locals=server_locals, thread_prefix=thread_prefix, task_metadata=task_metadata, 
            futures_metadata=futures_metadata, thread_pool=thread_pool, allow_get=allow_get)),
        (r"/tasks", TasksHandler, dict(task_metadata=task_metadata, allow_get=allow_get)),
        (r"/state", StateHandler, dict(get_endpoint_paths=get_endpoint_paths, 
            task_metadata=task_metadata, thread_pool=thread_pool, 
            websocket_connections=websocket_connections, allow_websocket=allow_websocket, 
            allow_get=allow_get)),
        ]

    # if @index_file is not None, add an IndexHandler to @_endpoint_list.
    if index_file is not None:
        logger.info("Adding IndexHandler for file: {}".format(index_file))
        index_handler = (r"/", IndexHandler, dict(index_file=index_file, 
            render_object=render_object, server_locals=server_locals))
        _endpoint_list.append(index_handler)

    # if @filesystem_path is not None, add a FilesystemHandler to @_endpoint_list.
    if filesystem_path is not None:
        logger.info("Adding FilesystemHandler for directory: {}".format(filesystem_path))
        filesystem_handler = (r"/filesystem", FilesystemHandler, dict(parent_path=filesystem_path, 
            allow_get=allow_get))
        _endpoint_list.append(filesystem_handler)

    # if @allow_websocket is True, add a WebsocketHandler to @_endpoint_list.
    if allow_websocket:
        logging.info("Adding WebsocketHandler.")
        websocket_handler = (r"/websocket", WebsocketHandler, dict(port=port, 
            websocket_connections=websocket_connections))
        _endpoint_list.append(websocket_handler)

    # create server.
    logger.info("Creating server at 'localhost:{}' with endpoints: {}".format(port,
        get_endpoint_paths()))
    app = web.Application(_endpoint_list)
    app.listen(port)
    ioloop.IOLoop.instance().start()
    
    return


if __name__ == "__main__":
    pass
