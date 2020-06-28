#!/usr/bin/python3

""" Placissimo Example 03: tests type enforcement. """

import logging
import sys

sys.path.append("..")

# set logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(
    # From the command line, Plac will enforce the types for each parameter as well as enforcing valid
    # choices for @string_choices; Placissimo will not.
    string: ("a string", "positional", None, str),
    integer: ("an int", "positional", None, int),
    floating: ("a float", "positional", None, float),
    string_choices: ("a string limited to choices", "positional", None, str, ["foo", "bar"]),
    string_option: ("a string option", "option", "s", str),
    integer_option: ("an integer option", "option", "i", int),
    floating_option: ("a float option", "option", "f", float),
    boolean_flag: ("a boolean flag", "flag", "b") = False,
):
    """Returns all user parameters."""

    vars = locals()
    print(vars)
    return vars


if __name__ == '__main__':
    import placissimo
    placissimo.call(main)
