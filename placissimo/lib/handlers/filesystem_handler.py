#!/usr/bin/python 3

""" This module contains a class that provides a RESTful API to access file and folder paths 
starting at a given parent path. """

# import modules.
import logging
import os
from datetime import datetime
from tornado import web


class FilesystemHandler(web.RequestHandler):
    """ This class provides a RESTful API to access file and folder paths starting at a given parent
    path. """


    def initialize(self, parent_path, allow_get):
        """ Initializes the @web.RequestHandler subclass. 

        Args:
            - parent_path (str): The absolute directory path at which file/folder browsing starts.
            - allow_get (bool): Use True to allow GET access. Otherwise, use False to restrict 
            access to POST-only requests.
        """

        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience functions to clean up path notation.
        self._normalize_sep = lambda p: p.replace(os.sep, os.altsep) if (os.altsep == "/") else p
        self._normalize_path = lambda p: self._normalize_sep(os.path.normpath(p)) if (
            p != "") else ""
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))

        # set attributes.
        self.parent_path = self._normalize_path(parent_path)
        self.allow_get = allow_get
        

    def _get_folder_contents(self, directory=None, exclude=None):
        """ Gets file and folder contents and metadata for @directory.
        
        Args:
            - directory (str): The directory path for which to send content metadata. If None,
            @self.parent_path is assumed.
            - exclude (str): Use "files" to remove files from the return value. Use "folders" to
            remove folders instead. Use and empty string to return both files and folders.

        Returns:
            dict: The return value.
            The file and folder metadata for @directory. If the path doesn't exists, 422 is 
            returned. If the path is an ancestor of @self.parent_path, or is otherwise out of 
            bounds, 403 is returned.

        Raises:
            - ValueError: If the value of @exclude is not one of: None, "files", or "folders". 
        """
        
        # if @directory is None make it an empty string so os.path operations can occur.
        if directory is None:
            directory = ""

        # if @exclude has an illegal value, raise an error.
        legal_excludes = ["files", "folders"]
        if exclude is not None and exclude not in legal_excludes:
            msg = "The  @exclude value must be one of '{}'; got: {}".format(legal_excludes, exclude)
            self.logger.error(msg)
            raise ValueError(msg)

        # join @directory with @parent_path.
        directory = self._join_paths(self.parent_path, directory)
        self.logger.info("Requested folder: {}".format(directory))
        if exclude == "files":
            self.logger.info("Files will be excluded from the response.")
        elif exclude == "folders":
            self.logger.info("Folders will be excluded from the response.")

        # make sure @directory is a folder. If not, send a 422. If it's an ancestor of 
        # @self.parent_path or otherwise out of bounds, send a 403.
        if not os.path.isdir(directory):
            self.logger.warning("Can't find folder: {}".format(directory))
            return 422
        elif not directory.startswith(self.parent_path):
            self.logger.warning("Forbidden folder request: {}".format(directory))
            return 403
        
        # create a dict of folder content metadata to send.
        folder_contents = {}
        for content in os.listdir(directory):

            # get the complete path to @content.
            path = self._join_paths(directory, content)

            # determine the containing folder path relative to @self.parent_path.
            container = os.path.relpath(directory, self.parent_path)
            container  = self._normalize_path(container)
            
            # skip @content as needed per @exclude.
            is_folder = os.path.isdir(path)
            if exclude == "files" and not is_folder:
                continue
            elif exclude == "folders" and is_folder:
                continue

            # update @folder_contents.
            content_stats = os.stat(path)
            size_in_bytes = content_stats.st_size if not is_folder else None
            creation_date = datetime.fromtimestamp(content_stats.st_ctime).isoformat()

            # add an absolute path and make @path relative to @self.parent_path.
            full_path = path
            path = os.path.relpath(path, self.parent_path)
            path = self._normalize_path(path)

            # create dict to return.
            folder_contents[content] = dict(container=container, is_folder=is_folder, 
                path=path, full_path=full_path, size_in_bytes=size_in_bytes, 
                creation_date=creation_date)

        return folder_contents


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

        # get the arguments to use.
        path = self.get_query_argument("path", default=None)
        exclude = self.get_query_argument("exclude", default=None)

        # send @path's contents.
        contents = self._get_folder_contents(path, exclude)
        if isinstance(contents, int):
            self.send_error(contents)
            return
        self.write(contents)
        self.finish()
        
        return


    @web.asynchronous
    def post(self):
        """ Implements POST requests. 
        
        Returns:
            None
        """

        # get the arguments to use.
        path = self.get_argument("path", default=None)
        exclude = self.get_argument("exclude", default=None)

        # send @path's contents.
        contents = self._get_folder_contents(path, exclude)
        if isinstance(contents, int):
            self.send_error(contents)
            return
        self.write(contents)
        self.finish()
        
        return


if __name__ == "__main__":
    pass
