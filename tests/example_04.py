#!/usr/bin/python3

""" Placissimo Example 04: writes a file. """

import os
import sys

sys.path.append("..")


def main(fname: ("a base filename",  "positional", None, str)):
    """Writes @fname to file."""

    if fname != os.path.basename(fname):
        raise ValueError("Use only a file basename, not: {}".format(fname))
    if os.path.splitext(fname)[-1] == "":
        raise ValueError("File extension may not be null.")
    if os.path.isfile(fname):
        raise FileExistsError("Wont't overwrite existing file.")

    with open(fname, "w") as f:
        pass

    is_file = os.path.isfile(fname)
    return is_file


if __name__ == '__main__':
    import placissimo
    placissimo.call(main)
