#!/usr/bin/python 3

""" Placissimo Example 05: tests the callback. """

# import modules.
import sys; sys.path.append("..")


# A default value of None is set for the callback variable @server_dict so that it still works from
# the command line without being used. This also prevents the API from expecting the argument to be 
# passed as a URL paramater.
#
# Making the var "positional" and setting the "metavar" to an empty string prevents @server_dict
# from showing up in the help message when passing "-h". For more information on metavars, see: https://micheles.github.io/plac/#more-features.
#
# But Placissimo will add all the annotation for you if you set this var to be the @callback_arg in 
# placissimo.call(..., callback_arg="server_dict") and if you omit adding an annotation of your own.
def main(name:("your name"), 
    surname:("your last name", "option")="",
    uppercase:("uppercase your name", "flag")=False,
    #server_dict:("", "positional", None, dict, None, "")=None, # manually add annotation.
    server_dict=None, # omit annotation and let Placissimo do it for you.
    ):
    """Prints @name if used as a command line script.
Adds server task names if called from a server."""

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