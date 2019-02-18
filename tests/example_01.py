#!/usr/bin/python 3

""" Placissimo Example 01: shows folder contents using os.listdir(). """

# import modules.
import sys; sys.path.append("..")
import logging
import os
import time
from datetime import datetime

# set logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(path: ("path to a folder"),
	        iso: ("use ISO format for time", "flag", "iso")=False,):
    """Returns @path contents and the time after a delay of 3 seconds."""

    logger.info("Getting contents for: {}".format(path))
    
    # add delay (gives time to switch to a browser and view logging).
    logger.debug("Sleeping for 3 seconds.")
    time.sleep(3)
    logger.debug("Done sleeping.")

    # get folder contents.
    contents = os.listdir(path)

    # get time.
    now = datetime.now()
    if iso:
        now = now.isoformat()
    else:
        now = now.ctime()

    data = contents, now
    print("Results: {}".format(data))
    return data


if __name__ == "__main__":
    import placissimo
    placissimo.call(main, render_object=__doc__)