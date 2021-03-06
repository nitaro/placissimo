#!/usr/bin/python3

""" This module contains a class that provides a RESTful API to access file and folder paths 
starting at a given parent path. 

Todo:
    * Consolidate redundant logic in GET/POST.
    * Needs full_path, rel_path, AND base_path fields.
"""

# import modules.
import os
from .base_handler import BaseHandler
from datetime import datetime
from tornado import web


class FilesystemHandler(BaseHandler):
    """ This class provides a RESTful API to access file and folder paths starting at a given parent
    path. """

    def initialize(self, **server_locals):

        super().initialize(__name__, **server_locals)

        # function to enforce Unix style paths.
        self.normpath = lambda p: os.path.normpath(p).replace("\\", "/")

        # set additional attributes.
        self.parent_path = self.normpath(self.filesystem_path)

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
            msg = "The  @exclude value must be one of '{}'; got: {}".format(
                legal_excludes, exclude)
            self.logger.error(msg)
            raise ValueError(msg)

        # join @directory with @parent_path.
        directory = os.path.join(self.parent_path, directory)
        directory = self.normpath(directory)

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
            self.logger.warning(
                "Forbidden folder request: {}".format(directory))
            return 403

        # create a dict of folder content metadata to send.
        folder_contents = {}
        for content in os.listdir(directory):

            # get the complete path to @content.
            full_path = os.path.join(directory, content)
            full_path = self.normpath(full_path)

            # skip @content as needed per @exclude.
            is_folder = os.path.isdir(full_path)
            if exclude == "files" and not is_folder:
                continue
            elif exclude == "folders" and is_folder:
                continue

            # update @folder_contents.
            content_stats = os.stat(full_path)
            size_in_bytes = content_stats.st_size if not is_folder else None
            creation_date = datetime.fromtimestamp(
                content_stats.st_ctime).isoformat()

            # get the relative version of @full_path.
            path = os.path.relpath(full_path, self.parent_path)
            path = self.normpath(path)

            # get the containing folder relative to @self.parent_path.
            container = os.path.relpath(directory, self.parent_path)
            container = self.normpath(container)

            # create dict to return.
            folder_contents[content] = dict(is_folder=is_folder, size_in_bytes=size_in_bytes,
                                            creation_date=creation_date, path=path, full_path=full_path, container=container,
                                            full_container=directory)

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
