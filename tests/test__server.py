#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import inspect
import json
import logging
import requests
import time
import unittest
import webbrowser
import launch_server

# enable logging.
logging.basicConfig(level=logging.DEBUG)   


class Test_Server(unittest.TestCase):
    """ Tests basic server connections. """
    
    def setUp(self):
        
        # import server args from @launch_server.
        self.funk = launch_server.FUNK
        self.render_object = launch_server.RENDER_OBJECT
        self.allow_broadcasts = launch_server.ALLOW_BROADCASTS
        self.allow_get = launch_server.ALLOW_GET
        self.allow_websocket = launch_server.ALLOW_WEBSOCKET
        self.filesytem_path = launch_server.FILESYSTEM_PATH
        self.index_file = launch_server.INDEX_FILE
        self.port = launch_server.PORT
    
        # launch server.
        launch_server.main()

		
    def _obtain_results(self, method=requests.get):
        """ Calls @self.funk via /api using @method. """

        # make the call; get the task's thread name.
        call = method("http://localhost:{}/api?path=.".format(self.port))
        callback = json.loads(call.text).keys()
        task_thread_name = list(callback)[-1]
        
        # check for /api results every 5 seconds.
        while True:
            time.sleep(5)
            task_data = requests.get("http://localhost:{}/tasks?name={}".format(self.port, 
                task_thread_name))
            task_data = json.loads(task_data.text)
            
            # get the first item in results (i.e. the list of files/folders in the path).
            if "done" in task_data[task_thread_name]:
                call_results = task_data[task_thread_name]["result"][0]
                logging.debug("requests.{}() results: {}".format(method.__name__, call_results))
                return call_results

        return

    
    def test__index(self):
        """ Does /index return a 200 via GET? """
        
        endpoint = "http://localhost:{}".format(self.port)
        logging.info("Testing endpoint: {}".format(endpoint))
        
        passed = requests.get(endpoint).status_code == 200
        self.assertTrue(passed)


    def test__api(self):
        """ Does /api return a 200 via GET? """

        endpoint = "http://localhost:{}/api".format(self.port)
        logging.info("Testing endpoint: {}".format(endpoint))
        
        passed = requests.get(endpoint).status_code == 200
        self.assertTrue(passed)


    def test__tasks(self):
        """ Does /tasks return a 200 via GET? """

        endpoint = "http://localhost:{}/tasks".format(self.port)
        logging.info("Testing endpoint: {}".format(endpoint))
        
        passed = requests.get(endpoint).status_code == 200
        self.assertTrue(passed)


    def test__state(self):
        """ Does /state return a 200 via GET? """

        endpoint = "http://localhost:{}/state".format(self.port)
        logging.info("Testing endpoint: {}".format(endpoint))
        
        passed = requests.get(endpoint).status_code == 200
        self.assertTrue(passed)


    def test__render(self):
        """ Does /index contain the proper rendered object?
        This queries /index via POST. """
        
        endpoint = "http://localhost:{}".format(self.port)
        logging.info("Testing /index for render object: {}".format(self.render_object))
        
        passed = self.render_object in requests.post(endpoint).text
        self.assertTrue(passed)


    def test__api_results(self):
        """ Do the results from calling @self.funk via /api match VS calling it directly? """

        logging.info("Testing /api results.")

        # call @self.funk() directly via Python.
        python_results = self.funk(path=".")[0]
        logging.debug("Python call results: {}".format(python_results))

        # call @self.funk() via GET and POST.
        get_results = self._obtain_results()
        post_results = self._obtain_results(requests.post)

        self.assertEqual(get_results, post_results, python_results)

    
    def test__socket_connection(self):
        """ Does the number of websocket connections increase by 1 after a browser connection?
        This queries /state via POST. """

        # make sure there's a browser to launch.
        try:
            webbrowser.browser
        except AttributeError:
            logging.warning("Can't find browser; skipping test: {}".format(inspect.stack()[0][3]))
            return

        # get number of websocket connections.
        get_connections = lambda: int(
                json.loads(
                    requests.post("http://localhost:{}/state".format(self.port)).text
                    ).get("websocket_connections")
                )
        
        current_connections = get_connections()
        logging.info("Current number of socket connections: {}".format(current_connections))
        
        logging.info("Connecting to host with the default browser.")
        webbrowser.open("http://localhost:{}".format(self.port))
        time.sleep(10)
        
        new_connections = get_connections()
        logging.info("New number of socket connections: {}".format(new_connections))

        passed = new_connections == current_connections + 1
        self.assertTrue(passed)
        

if __name__ == "__main__":
    pass