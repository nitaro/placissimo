#!/usr/bin/python3

""" This module contains a class that provides a websocket interface to logging statements. 

Todo:
    * If you implement secure cookies you might needs to work on @self.check_origin; see:
    "https://www.tornadoweb.org/en/stable/websocket.html?highlight=check_origin#tornado.websocket.WebSocketHandler.check_origin".
    * You need to investigate more options for websockets per: https://www.tornadoweb.org/en/stable/websocket.html.
"""

# import modules.
import logging
import urllib
from tornado import websocket


class WebsocketHandler(websocket.WebSocketHandler):
    """ This class provides a websocket interface to logging statements. """

    def initialize(self, **server_locals):

        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set server-only logger (i.e. hidden from websockets).
        self.server_logger = logging.getLogger(__name__ + ".server_logger")
        self.server_logger.addHandler(logging.NullHandler())

        # set attributes.
        self.server_locals = server_locals
        for k, v in server_locals.items():
            setattr(self, k, v)

    def check_origin(self, origin):
        """ Restricts websocket connections to localhost.
        See also: "https://www.tornadoweb.org/en/stable/_modules/tornado/websocket.html#WebSocketHandler.check_origin". """

        # check if origin is localhost.
        origin_netloc = urllib.parse.urlparse(origin).netloc
        is_localhost = origin_netloc.startswith("localhost") or origin_netloc.startswith(
            "127.0.0.1")

        # log a warning if an outside connection attempt is made.
        if not is_localhost:
            self.server_logger.warning("Illegal socket connection attempt made from: {}".format(
                origin_netloc))

        return is_localhost

    def open(self):
        """ Adds a new connection to @self.websocket_connections. """

        if self not in self.websocket_connections:
            self.server_logger.info(
                "Adding new websocket client: {}".format(self))
            self.websocket_connections.append(self)

        return

    def on_close(self):
        """ Removes a closed connection from @self.websocket_connections. """

        if self in self.websocket_connections:
            self.server_logger.info(
                "Removing closed websocket client: {}".format(self))
            self.websocket_connections.remove(self)

        return

    def on_message(self, message):
        """ Sends the client's message to the websocket as a log statement. If the client 
        requests a particular, valid logging level, the logging statement will use the requested
        level.

        Args:
            - message (str): The client's message to return. To invoke a particular logging level,
            preface this value with a valid logging level plus a colon, e.g. "info:My Message.".
        """

        self.server_logger.info(
            "Received message '{}' from client: {}".format(message, self))

        # create the message to send.
        message_wrap = "Websocket client {} said: {}".format(self, message)

        # determine the implicit logging level.
        level = message[:message.find(":")].lower()

        # make sure @level is a valid logging level.
        if level not in ["debug", "info", "warning", "error", "critical"]:
            level, message = "info", message
        else:
            message = message.split(":", 1)[1].strip()

        # log the message per @level.
        # Note: make sure any "extra" args are reflected in ../log_manager:_WebsocketHandler.emit().
        self.server_logger.debug(
            "Logging message with implicit level of: {}".format(level))
        getattr(self.logger, level)(message_wrap, extra={"socketSender": self,
                                                         "socketMessage": message})

        return


if __name__ == "__main__":
    pass
