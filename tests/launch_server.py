#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import requests
from concurrent.futures import ProcessPoolExecutor
import placissimo
import example_01

# enable logging.
logging.basicConfig(level=logging.DEBUG) 

# set args for @placissimo.serve().
FUNK = example_01.main
RENDER_OBJECT = example_01.__doc__
PORT = 5000
INDEX_FILE = placissimo.index_file
FILESYSTEM_PATH = ".."
ALLOW_WEBSOCKET = True
ALLOW_BROADCASTS = True
ALLOW_GET = True

# create process pool.
PROCESS_POOL = ProcessPoolExecutor()


# launch the server.
def launch(*args, **kwargs):

    logging.info("Launching server.")
    placissimo.serve(*args, **kwargs)
    
    return


# run @launch if a server is not already running.
def main(funk=FUNK, render_object=RENDER_OBJECT, port=PORT,
    index_file=INDEX_FILE, filesystem_path=FILESYSTEM_PATH, allow_websocket=ALLOW_WEBSOCKET, 
    allow_broadcasts=ALLOW_BROADCASTS, allow_get=ALLOW_GET, *args, **kwargs):

    host = "http://localhost:{}".format(port)

    logging.info("Testing connection to: {}".format(host))
    try:
        requests.get(host)
        logging.info("Connection exists for host: {}".format(host))
    except requests.ConnectionError:
        logging.info("Connection does not exist for host: {}".format(host))
        PROCESS_POOL.submit(launch, funk=funk, render_object=render_object, port=port, 
            index_file=index_file, filesystem_path=filesystem_path, allow_websocket=allow_websocket, 
            allow_broadcasts=allow_broadcasts, allow_get=allow_get, *args, **kwargs)

    return


if __name__ == "__main__":
    main()
