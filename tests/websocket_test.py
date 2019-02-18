#!/usr/bin/env python3

""" This can be used to test private VS broadcast messaging in websockets.

1. Do either:
        py -3 websocket_test.py --servissimo -allow-get -index-file="websocket_test.html" -websocket-mode=broadcast 
    or with:
        -websocket-mode=private

2. Open two browsers at localhost:8080.
3. Call the /api endpoint.
4. Call the /tasks endpoint.
5. If broadcasting was used, then the results should be 2 private messages and 4 broadcast messages.
Without broadcasts, the results should be 2 private messages and only 2 broadcast messages.
"""


# import modules.
import sys; sys.path.append("..")
import logging
import os
import placissimo

# set data file.
DATA_FILE = "websocket_test.txt"


# this filter will keep track of messages from and between websockets.
class ModeFilter(logging.Filter):

    def __init__(self, data_file):

        if os.path.isfile(data_file):
            os.remove(data_file)
        self.data_file = open(data_file, "a")
        
    
    def filter(self, record):
        socketMessage = record.__dict__.get("socketMessage")
        if socketMessage is not None:
            if socketMessage == "private_mode":
                self.data_file.write("private")
                self.data_file.flush()
            elif socketMessage == "broadcast_mode":
                self.data_file.write("broadcast")
                self.data_file.flush()

        return True


# counts how many private and broadcast messages exist.
def main():

    results = ""
    try:
        with open(DATA_FILE) as f:
            results = f.read()
    except FileNotFoundError:
        pass
    
    results = "Private messages: {}; Broadcast messages: {}".format(results.count("private"),
        results.count("broadcast"))
    return results


if __name__ == "__main__":
    mode_filter = ModeFilter(DATA_FILE)
    placissimo.call(main, socket_filters=[mode_filter])