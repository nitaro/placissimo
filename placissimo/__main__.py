#!/usr/bin/python 3

""" Placissimo is a Plac intensifier.

It allows you to run a function from the command line or through a RESTful HTTP server. The function
just needs to be annotated as per Plac.

For information on Plac, see: https://pypi.org/project/plac/. """

# import modules.
import logging
import os
import plac
import sys
from .lib import dependency_error
from .lib import log_manager
from .lib import server

# create logger.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def call(funk, server_name="servissimo", render_object=None, callback_arg=None, max_threads=None, 
    socket_filters=None, *args, **kwargs):
    """ Provides an iterface to @funk via the command line or an HTTP server.

    Args:
        - funk (function): The user function.
        - server_name (str): The string that serves as the command line trigger to launch the 
        server. This value is also the prefix for the HTTP server's thread names. Use only letters.
        - render_object (object): Any object to pass to the rendered HTML file.
        - callback_arg (str): The name of the argument for @funk to which to pass back
        placissimo.server.serve()'s non-private local vars. Use None to omit passing anything back 
        to @funk.
        - max_threads (int): The number of concurrent threads to support. If None, the value will be
        based on your CPU per: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor.
        - socket_filters (list): Logging filters to add to the websocket logger. Each item in the 
        list must be an instance of logging.Filter. Use None if no filters are needed.

    Returns:
        None

    Raises:
        - ValueError: If @callback_arg is not an actual argument within @funk.
        - Exception: If @funk can't be wrapped then the given exception is raised. But if the 
        exception is "dependency_error.DependencyError", then sys.exit() is called.
    """

    # if @callback_arg is not None and has no annotations, add annotations to hide it from Plac's
    # command line help message.
    if callback_arg is not None:
        if callback_arg not in funk.__code__.co_varnames:
            msg = "Callback argument '{}' does not appear in the function's arglist: {}".format(
                callback_arg, funk.__code__.co_varnames)
            logger.error(msg)
            raise ValueError(msg)
        elif funk.__annotations__.get(callback_arg) is None:
            funk.__annotations__[callback_arg] = ("", "positional", None, None, None, "")
    
    # get name of calling module.
    caller = os.path.basename(sys.argv[0])

    # if @arglist was passed to @call() use it, otherwise use sys.argv sans the script itself.
    if "arglist" in kwargs:
        arglist = kwargs["arglist"]
        kwargs.pop("arglist")
    else:
        arglist = sys.argv[1:]

    # create a default wrapper function that assumes the CLI will be used.
    wrapper = (lambda: plac.call(funk, arglist, *args, **kwargs))

    # set the trigger phrase to launch the server.
    trigger = "--{}".format(server_name)

    # alter @wrapper as needed per the presence or absence of @trigger in sys.argv.
    if trigger not in sys.argv:
        
        # update the .epilog attribute to include server details.
        addendum = "\n\nserver usage: {} {} -h".format(caller, trigger)
        funk.epilog = addendum if not hasattr(funk, "epilog") else "{}{}".format(
            funk.epilog.format(), addendum)
    
    else:

        # remove @trigger from command line arguments.
        arglist.remove(trigger)
        
        # set @main() annotations per "https://micheles.github.io/plac/#plac-vs-argparse".
        main.prog = "{} {}".format(caller, trigger)
        
        # get required parameters from @main (port number, etc.).
        port, index_file, filesystem_path, allow_websocket, allow_broadcasts, allow_get = plac.call(
            main, arglist, *args, **kwargs)
        
        # update @wrapper to launch a server.
        wrapper = (lambda: server.serve(funk, server_name, render_object, callback_arg, max_threads, 
            socket_filters, port, index_file, filesystem_path, allow_websocket, allow_broadcasts, 
            allow_get, *args, **kwargs))

    # run @wrapper.
    try:
        wrapper()
    except dependency_error.DependencyError as err:
        sys.exit(err)
    except Exception:
        raise

    return


def main(allow_get: ("enable GET access", "flag"), 
        websocket_mode: ("options for the \"/websocket\" endpoint", "option", None, None, 
            ("private", "broadcast")),
        filesystem_path: ("path to parent directory for the \"/filesystem\" endpoint", "option",
            None, str)=None,
        index_file: ("path to HTML template for the \"/\" endpoint \
            (use \"DEFAULT\" to use the built-in file)", "option", None, str)=None,
        port: ("port number to use", "option", None, int)=8080,
        ):
    
    """Server options."""

    # determine websocket configuration.
    allow_websocket, allow_broadcasts = False, False
    if websocket_mode is not None:
        allow_websocket = True
        allow_broadcasts = (websocket_mode == "broadcast")

    # if needed, use built-in HTML template.
    if index_file == "DEFAULT":
        index_file = os.path.join(os.path.dirname(__file__), "lib", "index.html")
    
    return (port, index_file, filesystem_path, allow_websocket, allow_broadcasts, allow_get)


if __name__ == "__main__":
    pass
