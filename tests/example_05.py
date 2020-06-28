#!/usr/bin/python3

""" Placissimo Example 05: tests the callback. """

import sys

sys.path.append("..")


def main(name: ("your name"),
         surname: ("your last name", "option") = "",
         uppercase: ("uppercase your name", "flag") = False,
         # server_dict:("", "positional", None, dict, None, "")=None, # manually add annotation.
         server_dict=None,  # omit annotation and let Placissimo do it for you.
         ):
    """Prints @name if used as a command line script. Adds server task names if called from a server."""

    # finalize @name.
    name = "{} {}".format(name, surname)
    if uppercase:
        name = name.upper()

    if server_dict is None:
        # command line was used.
        print(name)
    else:
        # server was used because the callback was received.
        # must be JSON-safe because this is returned to the "/tasks" endpoints, hence str().
        tasks = str(server_dict["task_metadata"].keys())
        return (name, tasks)


if __name__ == '__main__':
    import placissimo
    placissimo.call(main, callback_arg="server_dict")
