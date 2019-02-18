#!/usr/bin/python 3

""" This module contains functions to update stream and websocket handling for the root logger. """

# import modules.
import json
import logging
import tornado


class _WebsocketFilter(logging.Filter):
    """ Removes log records sent by low-level server modules (Tornado, asyncio, etc.). """


    def __init__(self):
        """ Sets instance attributes. """

        # establish loggers to ignore.
        self.ignore_by_starts = ["asyncio", "tornado"]
        self.ignore_by_ends = [".private_logger"]

    def filter(self, record):
        """ Removes all records sent by any logger found in @self.ignore_by_starts or 
        @self.ignore_by_ends. """

        for ignore_by_start in self.ignore_by_starts:
            if record.name.startswith(ignore_by_start):
                return False
        for ignore_by_end in self.ignore_by_ends:
            if record.name.endswith(ignore_by_end):
                return False
        
        return True


class _WebsocketHandler(logging.StreamHandler):
    """ This class creates a logging handler for websockets. It sends the entire logging records's 
    __dict__ attribute (encoded as JSON) to each client. If a given item within the record is not 
    JSON-compatible, the item is converted to a string prior to sending. """

    # WARNING: Do not attempt any logging statements inside this class; use print() if needed.
    
    def __init__(self, websocket_connections, allow_broadcasts):
        """ Initializes the base StreamHandler class with additional attributes.  
        
        Args:
            - websocket_connections (list): All connected websocket clients. Each item is an 
            instance of placissimo.lib.handlers.websocket_handler.WebsocketHandler. This will be 
            None if websockets are not used.
            - allow_broadcasts (bool): Use True to allow messages sent by a given websocket client
            to be broadcast to all other connected clients.
        """

        super().__init__()
        self.websocket_connections = websocket_connections
        self.allow_broadcasts = allow_broadcasts


    def emit(self, record):
        """ Sends the logging @record to clients in @self.websocket_connections. """

        # loop through each client.
        for ws_con in self.websocket_connections:

            # add socket information to the record.
            record.socketClient = ws_con
            record.socketConnections = self.websocket_connections

            # add extra fields per ./handlers/websocket_handler:WebsocketHandler.on_message().
            # setting None for these indicates that the server is the sender.
            if not hasattr(record, "socketSender"):
                record.socketSender, record.socketMessage = None, record.msg

            # if needed, prevent logging to clients other than the sending client or the server.
            if not self.allow_broadcasts:
                if record.socketClient != record.socketSender and record.socketSender is not None:
                    continue

            # JSON-encode @record.__dict__.
            msg = json.dumps(record.__dict__, default=lambda obj: str(obj))
            
            # broadcast @msg to the client if it's not already closed.
            try:
                ws_con.write_message(msg)
                self.flush()
            except tornado.websocket.WebSocketClosedError:
                pass
            except Exception as err:
                msg  = "\n*** Can't send message '{}' to client '{}' due to error: {}\n\n".format(
                    record, ws_con, err.__repr__())
                print(msg, flush=True)
        
        return



def handle_streams():
    """ Removes any existing stream handlers for the root logger and adds a new, root stream 
    handler. 
    
    Returns:
        None
    """

    # set logging level for @logging.root.
    logging.root.setLevel(logging.DEBUG)
    
    # create/add handler and formatter for console.
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(
        "%(asctime)s - %(threadName)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s")
    stream_handler.setFormatter(stream_formatter)
    logging.root.addHandler(stream_handler)
    logging.debug("Added logging.StreamHandler object: {}".format(stream_handler))

    # remove all other logging stream handlers.
    logging.debug("Removing any previous logging.StreamHandler objects.")
    for handler in logging.root.handlers:
        if isinstance(handler, logging.StreamHandler):
            if handler == stream_handler:
                continue
            logging.debug("Removing StreamHandler object: {}".format(handler))
            logging.root.removeHandler(handler)

    return


def handle_sockets(websocket_connections, allow_broadcasts, socket_filters):
    """ Adds a websocket logging handler to the root logger.
    
    Args:
        - websocket_connections (list): All connected websocket clients. Each item is an instance of
        placissimo.lib.handlers.websocket_handler.WebsocketHandler. This will be None if websockets
        are not used.
        - allow_broadcasts (bool): Use True to allow messages sent by a given websocket client to be
        broadcast to all other connected clients.
        - socket_filters (list): Logging filters to add to the websocket logger. Each item in the 
        list must be an instance of logging.Filter. Use None if no filters are needed.
    
    Returns:
        None

    Raises:
        - TypeError: If an item in @socket_filters is not an instance of logging.Filter.
    """
    
    # if websockets will not be used, return.
    if websocket_connections is None:
        return

    # otherwise, create a websocket logging handler.
    preposition = "with" if allow_broadcasts else "without"
    logging.info("Adding logging handler for websockets {} broadcasts.".format(preposition))
    websocket_handler = _WebsocketHandler(websocket_connections, allow_broadcasts)
    websocket_filter = _WebsocketFilter()
    websocket_handler.addFilter(websocket_filter)
    
    # if needed, add custom @socket_filters to the handler.
    if socket_filters is not None:

        logging.info("Adding custom filters to websocket logger.")
        
        for filter in socket_filters:
            logging.debug("Adding filter item number: {}".format(socket_filters.index(filter)))
            if isinstance(filter, logging.Filter):
                websocket_handler.addFilter(filter)
            else:
                msg = "Can't add logging filter with type: {}".format(type(filter))
                logging.error(msg)
                raise TypeError(msg)

    # add the websocket logging handler to the root logger.
    logging.root.addHandler(websocket_handler)
 
    return


if __name__ == "__main__":
    pass
