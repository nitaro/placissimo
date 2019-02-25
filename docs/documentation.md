# Placissimo Documentation #

**Placissimo** is designed to augment the `plac.call()` function of [**Plac**](https://micheles.github.io/plac/) for Python 3+ scripts.

## Why Placissimo? ##
Let's say you have a function, `main()`. And you use `plac.call(main)` to provide an easy, elegant command line interface to `main()`.

But let's say that you *also* want the option to access `main()` over a RESTful HTTP server. That's the scenario in which you can use `placissimo.call(main)` instead.

*For a "quick start" guide, see `../README.md`.*

## Why Not Placissimo? ##
Placissimo is not intended to replace [advanced usages](https://micheles.github.io/plac/#advanced-usages-of-plac) or [experimental features](https://micheles.github.io/plac/#experimental-features) of Plac.

Other reason to avoid Placissimo:

- You are doing mission-critical work.
	- Placissimo isn't well tested at this time.
- You need a secure server.

## Installation ##
I've had more success installing the requirements first a la:

	pip3 -r requirements.txt

and *then* doing:

	pip3 install .

## Server Side ##
When you `import placissimo` you have access to three main objects:
  
1. `placissimo.call()`: Replaces `plac.call()`.
2. `placissimo.serve()`: Accepts your Python function and provides a RESTful interface to it.
	- This is called by `placissimo.call()` but can be used in native Python code if you don't need command line access.
3. `placissimo.index_file`: Absolute path to the built-in example HTML template, `./placissimo/lib/index.html`.

## Client Side ##
Clients can access up to six possible endpoints:

1. `/`*: Shows a rendered HTML file.
2. `/api`: Provides an interface to the function you handed to `placissimo.call()` or `placissimo.serve()`.
3. `/state`: Shows the application state and a list of enabled endpoints.
4. `/tasks`: Shows the status and results for calls to `/api`.
5. `/filesystem`*: Shows file and folder listings starting at a given parent folder.
6. `/websocket`*: Provides a websocket interface to send and receive logging statements.

*_Only available if explicitly requested._
 
### Endpoints ###
#### `/` ####
This endpoint is only available if you pass an [HTML template](https://www.tornadoweb.org/en/stable/template.html) via the command line or through Python code.

*Command line*:
	
	cd ../tests
	py -3 example_01.py --servissimo -index-file="../placissimo/lib/index.html"

*Python*:

	#!/usr/bin/python 3
	import placissimo, example_01
	placissimo.serve(funk=example_01.main, index_file=placissimo.index_file)

*The rendered HTML file is available via GET even if GET requests are not enabled for other endpoints.*

##### Renderable Objects #####
A Python dictionary called `server_locals` is always available to render from the template. It includes the function you handed to Placissimo, i.e. `{{ server_locals["funk"] }}`, and all non-private objects passed to and from `placissimo.serve()`.

If you need to pass in a custom Python object to your template, you can pass it via the `render_object` argument for `placissimo.call()` or `placissimo.serve()`. This can be referenced in the template as `{{ render_object }}`.

#### `/api` ####
##### Parameters #####
Parameters for this endpoint are determined by the function you handed to Placissimo.

Placissimo will internally convert parameter values that look like numbers to `int` or `float` objects. Likewise, capital `True` and `False` values will be converted to Python boolean objects. Everything else is a [string](https://youtu.be/_-8j8c7iL3E).

In other words, a request for `/api?myNumber=12&myBoolean=True` means that `myNumber` and `myBoolean` are converted to respective `int` and `bool` objects before being sent to your function.

*Unlike Plac, Placissimo does not use argument annotations to enforce data types or valid choices. Also unlike Plac, "optional" command line arguments must still be explicitly requested via GET or POST. See `../tests/example_03.py` for some related demo code.*

##### Response #####
	{
	    "servissimo_001": {
	        "caller": "example_01.py.main",
	        "start_time": "2019-02-14T10:00:30.300222",
	        "running": true,
	        "done": false
	    }
	}

#### `/state` ####
##### Parameters #####
None

##### Response #####
	{
	    "endpoints": [
	        "/",
	        "/api",
	        "/filesystem",
	        "/state",
	        "/tasks",
	        "/websocket"
	    ],
	    "running_threads": 0,
	    "available_threads": 20,
	    "websocket_connections": 0
	}

#### `/tasks` ####
##### Parameters #####
This endpoint takes an optional parameter, `name`.

By requesting a valid task identifier, e.g. `/tasks?name=servissimo_001`, the response is limited to metadata for the given task. Omitting the parameter will return metadata for all tasks.

##### Response #####
	{
	    "servissimo_001": {
	        "caller": "example_01.py.main",
	        "start_time": "2019-02-14T10:00:30.300222",
	        "running": false,
	        "done": true,
	        "end_time": "2019-02-14T10:00:33.325225",
	        "result": [
	            [
	                "example_01.py",
	                "example_02.py",
	                ...
	            ],
	            "Thu Feb 14 10:00:33 2019"
	        ],
	        "exception": null
	    }
	}

The following keys are omitted from the response while `done=false`:

 1. end_time
 2. result
 3. exception

#### `/filesystem` ####
This endpoint is only available if a starting path is passed via the command line or through Python code.

*Command line*:
	
	cd ../tests
	py -3 example_01.py --servissimo -filesystem-path="."

*Python*:

	#!/usr/bin/python 3
	import placissimo, example_01
	placissimo.serve(funk=example_01.main, filesystem_path=".")

*Users can pass in a starting path using either relative or absolute path notation.*

##### Parameters #####
This endpoint takes two optional parameters, `path` and `exclude`.

The value for `path` must be a valid folder name path relative to the starting path. For example, `/filesystem?path=bar/baz` would return contents for `/foo/bar/baz` if `/foo` is the starting path.

Omitting the `path` parameter will return contents for the starting path.

To return only file names in the response, use `exclude=folders`. Likewise, use `exclude=files` to return only folder names.

Omitting the `exclude` parameter will return both files and folders.

*Examples*:

- `/filesystem?path=bar/baz`
- `/filesystem?exclude=folders`
- `/filesystem?path=bar/baz&exclude=files`

##### Response #####
	{
	    "example_01.py": {
	        "container": ".",
	        "is_folder": false,
	        "path": "example_01.py",
		"full_path": "D:/placissimo-dev/tests/example_01.py",
	        "size_in_bytes": 1110,
	        "creation_date": "2018-10-15T14:46:24.095074"
	    },
		...
	    "__pycache__": {
	        "container": ".",
	        "is_folder": true,
	        "path": "__pycache__",
		"full_path": "D:/placissimo-dev/tests/__pycache__",
	        "size_in_bytes": null,
	        "creation_date": "2019-02-02T10:14:01.100704"
	    }
	}

#### `/websocket` ####
This endpoint is only available if websockets are requested via the command line or through Python code.

*Command line*:
	
	cd ../tests
	py -3 example_01.py --servissimo -websocket-mode=broadcast -index-file=DEFAULT

*Python*:

	#!/usr/bin/python 3
	import placissimo, example_01
	placissimo.serve(funk=example_01.main, allow_websocket=True, allow_broadcasts=True, index_file=placissimo.index_file)

*Enabling the `/` endpoint along with websockets is required because cross-origin websocket connections are not allowed.*

##### Websocket Messages #####
Websocket messages are JSON-encoded [Python logging records](https://docs.python.org/3/library/logging.html#logrecord-objects).

Messages come from:

- Placissimo
	- This includes logging from imported modules as well as any logging from the function you passed to Placissimo.
- Websocket Clients
  - Messages can only be passed from client to client if broadcasting is enabled.

In addition to the standard record object, Placissimo adds four new fields:

1. `socketClient`: The identifier for the receiving websocket client.
2. `socketConnections`: The list of identifiers for all connected websocket clients.
3. `socketSender`: The identifier for the websocket client that sent the message.   
	- This is `null` if the message came from Placissimo, i.e not a client.
4. `socketMessage`: The logging message.

##### Receiving Messages #####
	// JavaScript
	var socket = new WebSocket("ws://localhost:8080/websocket");
	socket.onmessage = function (event) { // do something ...

##### Sending Messages #####
	// JavaScript
	var socket = new WebSocket("ws://localhost:8080/websocket");
	socket.send("Hello World");

Sent messages are assumed to be at the `logging.INFO` level.

To request a specific logging level, just preface the message with a valid Python logging level (lower case) followed by a colon:
	
	socket.send("debug:Hello World"); // sets the message level to logging.DEBUG.

If you request a logging level, the `socketMessage` value will equal the intended message:

	{
		...
		levelname: "DEBUG",
		"socketMessage": "Hello World",
		"message": "Websocket client <placissimo.lib.handlers.websocket_handler.WebsocketHandler object at 0x000001A2105AF0B8> said: debug:Hello World",
		...
	}

##### Tracking Tasks #####
As you already know, the `/api` endpoint returns a task identifier, e.g. `servissimo_001`.

This value will appear in the `threadName` field. This can be used to track logging statements that are derived from a specific call to your function.

	{
		...
		"threadName": "servissimo_001",
		"socketMessage": "Getting contents for: ."
		...
	}

## Callbacks ##
The same `server_locals` that can be rendered via an HTML template are available for a callback.

Callbacks can be used to determine if your function was run from the command line or via a server.

And there's no need to annotate your callback argument. Placissimo will automatically hide it from the command line's help messaging.

*Example:*

	def main(..., server_dict=None):
		
		if server_dict is None:
			# the command line was used.
			print("Hello World")
		else:
			# the server was used.
			return "Hello World"

	# pass in the the name of the argument you want to receive the callback from.
	placissimo.call(main, callback_arg="server_dict")

*For a little demo of using a callback, see `../tests/example_05.py`.*
