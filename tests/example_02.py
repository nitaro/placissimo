#!/usr/bin/python3

""" Placissimo Example 02: calls "dir" as a subprocess and runs the call as a new process. """

import logging
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.append("..")

# set logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create process pool.
PROCESS_POOL = ProcessPoolExecutor()


# call "dir"; return output.
def call_dir():
    cmd = subprocess.Popen("dir", shell=True, stdout=subprocess.PIPE)
    output = cmd.stdout.read()

    return output


def main():
    """Runs dir()."""

    call = PROCESS_POOL.submit(call_dir)
    while True:
        if call.done():
            result = call.result().decode()
            print("Results: \n\n{}".format(result))
            return result


if __name__ == "__main__":
    import placissimo
    placissimo.call(main)
