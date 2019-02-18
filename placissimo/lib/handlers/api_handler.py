#!/usr/bin/python 3

""" This module contains a class that provides a RESTful API to the function called by 
placissimo.call(). """

# import modules.
import ast
import asyncio
import logging
import os
import threading
from datetime import datetime
from tornado import web


class ApiHandler(web.RequestHandler):
    """ This class provides a RESTful API to the function called by placissimo.call(). """


    def initialize(self, funk, callback_arg, server_locals, thread_prefix, task_metadata, 
        futures_metadata, thread_pool, allow_get=True):
        """ Initializes the @web.RequestHandler subclass.
        
        Args:
            - funk (function): The user function.
            - callback_arg (str): The name of the argument for @funk to which to pass back
            placissimo.server.serve()'s non-private local vars. Use None to omit passing anything
            back to @funk.
            - server_locals (dict): The non-private local vars for placissimo.server.serve().
            - thread_prefix (str): The string to prefix threads with (e.g. "servissimo_").
            - task_metadata (dict): Keys are thread names, values are a dict with human-readable
            metadata about tasks, whether finished or not.
            - futures_metadata (dict): Keys are Futures, values are thread names.
            - thread_pool (concurrent.futures.ThreadPoolExecutor): The pool of task threads.
            - allow_get (bool): Use True to allow GET access. Otherwise, use False to restrict 
            access to POST-only requests.
        """

        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.funk = funk
        self.callback_arg = callback_arg
        self.server_locals = server_locals
        self.thread_prefix = thread_prefix
        self.task_metadata = task_metadata
        self.futures_metadata = futures_metadata
        self.thread_pool = thread_pool
        self.allow_get = allow_get


    def _convert_kwargs_items(self, kwargs_items):
        """ Converts each item in @kwargs_items to a string per "https://stackoverflow.com/a/10356004".

        Args:
            - kwargs_items (dict_items): The key/value pairs to evaluate.
        
        Returns:
            dict: The return value.
        """

        self.logger.debug("Coverting @kwargs_items to strings.")
        kwargs = {k: "".join([i.decode() for i in v]) for k,v in kwargs_items}
        
        return kwargs


    def _translate_kwargs(self, kwargs):
        """ Converts each value in @kwargs to the assumed type based on its value. For example,
        the string "True" is converted to a boolean True.
        
        Args:
            - kwargs (dict): The key/value pairs to evaluate.
        
        Returns:
            dict: The return value.
        """

        self.logger.info("Interpreting parameter types in URL: {}".format(kwargs))

        # interprets the implied type for an object.
        changed = []
        def _safe_eval(obj):
            try:
                obj = ast.literal_eval(obj)
                if obj.__class__.__name__ not in ["NoneType", "int", "float", "bool"]:
                    obj = str(obj)
                changed.append(obj)
            except:
                pass

            return obj

        # update values in @kwargs.
        for kwarg in kwargs:
            kwargs[kwarg] = _safe_eval(kwargs[kwarg])

        # report changes.
        self.logger.info("Number of changes to URL parameters: {}".format(len(changed)))
        if len(changed) != 0:
            self.logger.debug("Updated paramaters dict to: {}".format(kwargs))
        
        return kwargs


    def _update_task(self, task_future):
        """ This is the callback function for a given task. It updates the task's entry in 
        @self.task_metadata upon the task's completion.
        
        Args:
            - task_future (concurrent.futures._base.Future): The task for which metadata is to be 
            updated.

        Returns:
            None
        """

        # find the thread name for the given task.
        thread_name = self.futures_metadata[task_future]
        self.logger.debug("Updating task metadata for thread: {}".format(thread_name))

        # update the task's metadata dict.
        self.task_metadata[thread_name]["end_time"] = datetime.now().isoformat()
        self.task_metadata[thread_name]["running"] = task_future.running()
        self.task_metadata[thread_name]["done"] = task_future.done()
        try:
            self.task_metadata[thread_name]["result"] = task_future.result()
            self.task_metadata[thread_name]["exception"] = task_future.exception()
        except Exception as err:
            self.task_metadata[thread_name]["result"] = None
            self.task_metadata[thread_name]["exception"] = err.__repr__()
        
        return


    def _wrap_task(self, thread_name, **kwargs):
        """ This wraps @self.funk() so that its execution is contained within a given thread name.
        This forces its logs and all child logging to have the same thread name.
        
        Args:
            - thread_name (str): The unique thread name for a given task.
            - args/kwargs: The arguments to send to @self.funk().
            
        Returns:
            function: The return value.
            The wrapped and executed version of @self.funk(*args, **kwargs).
        """

        self.logger.debug("Wrapping function as thread: {}".format(thread_name))

        # without this, child logs of @self.funk() don't seem to appear.
        # fix per "https://github.com/tornadoweb/tornado/issues/2183#issuecomment-371001254".
        asyncio.set_event_loop(asyncio.new_event_loop())
        
        # set the current thread name.
        # note: this allows for consistent incrementing of the thread suffix (_0, _1, etc.) VS 
        # passing a "thread_name_prefix" argument to concurrent.futures.ThreadPoolExecutor because
        # the latter approach will result in restart the numbering from time to time.
        threading.current_thread().name = thread_name   
        
        return self.funk(**kwargs)


    def _start_task(self, **kwargs):
        """ Starts a new task via @self._wrap_task() and updates @self.task_metadata with a new 
        entry for the task.

        Args:
            - kwargs (dict): The arguments to send to @self._wrap_task().
        
        Returns:
            dict: The return value.
            The metadata for the started task.

        Raises:
            - RuntimeError: If an attempt is made to start a new task and the maximum number of 
            threads is already running.
        """

        self.logger.info("Adding task thread.")

        # if the max number of threads is already running, raise an error.
        running_threads = sum([1 for t in self.task_metadata 
            if not self.task_metadata[t].get("done")])
        if not running_threads < self.thread_pool._max_workers:
            msg = "Can't add task; already running {} maximum threads.".format(
                self.thread_pool._max_workers)
            self.logger.error(msg)
            raise RuntimeError(msg)
        else:
            self.logger.info("Now running {} out of {} maximum threads.".format(running_threads + 1, 
                self.thread_pool._max_workers))
    
        # create a new task identifier.
        task_id = len(self.task_metadata) + 1
        task_id = str(task_id).zfill(3)

        # create a new thread name and set the thread name.
        thread_name = "{}{}".format(self.thread_prefix, task_id)
        self.logger.info("Task is assigned to thread name: {}".format(thread_name))

        # create new metadata for the task.
        caller = os.path.basename(self.funk.__code__.co_filename)
        task_data = {"caller": "{}.{}".format(caller, self.funk.__name__), 
            "start_time": datetime.now().isoformat(), 
            "running": True, 
            "done": False}

        # update values in @kwargs.
        kwargs = self._translate_kwargs(kwargs)

        # if needed, add @self.callback_arg to @kwargs.
        if self.callback_arg is not None:
            if self.callback_arg in kwargs:
                msg = "Callback argument '{}' already exists in parameters".format(
                    self.callback_arg)
                msg += "; it will be overwritten."
                self.logger.warning(msg)
            self.logger.info("Passing server arguments as '{}' to function.".format(
                self.callback_arg))
            kwargs[self.callback_arg] = self.server_locals
        
        # add the task to @self.thread_pool.
        task_future = self.thread_pool.submit(self._wrap_task, thread_name, **kwargs)
        
        # add @task_future to @self.futures_metadata.
        self.futures_metadata[task_future] = thread_name

        # update @self.task_metadata.
        self.task_metadata[thread_name] = task_data
        
        # add a callback to @task_future so that its metadata can be updated upon completion.
        task_future.add_done_callback(self._update_task)
        
        # create a temporary metadata dict with @thread_name as the key.
        temp_md = {thread_name: task_data}
        
        return temp_md


    @web.asynchronous
    def get(self):
        """ Implements GET requests. If @self.allow_get is False, sends a 403.
        
        Returns:
            None
        """
        
        # if GET access is restricted, return an error.
        if not self.allow_get:
            self.logger.warning("GET requests are forbidden.")
            self.send_error(403)
            return
        
        # get parameters.
        kwargs = self._convert_kwargs_items(self.request.arguments.items())

        # start a task and send the task metadata.
        task_metadata = self._start_task(**kwargs)
        self.write(task_metadata)
        self.finish()

        return


    @web.asynchronous
    def post(self):
        """ Implements POST requests. 
        
        Returns:
            None
        """

        # get parameters.
        kwargs = self._convert_kwargs_items(self.request.arguments.items())

        # start a task and send the task metadata.
        task_metadata = self._start_task(**kwargs)
        self.write(task_metadata)
        self.finish()

        return

    
if __name__ == "__main__":
    pass
