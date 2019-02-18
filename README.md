# Introduzione #
**Placissimo** is a [**Plac**](https://pypi.org/project/plac/) intensifier.

It allows you to run a function from the command line or through a RESTful HTTP server. The function just needs to be annotated as per Plac.

## Stay Lazy My Friends ##
Just add "issimo" to `plac`:
	        
	#!/usr/bin/python 3
	
	# hello.py
	def main(name):
	    hello = "Hello {}".format(name)
	    print(hello)
	    return hello

	if __name__ == "__main__":
	    import placissimo # import plac
	    placissimo.call(main) # plac.call(main)

Use the command line as before:

	> py -3 hello.py -h
	> # shows help message including how to launch a server.
	> py -3 hello.py Placissimo
	Hello Placissimo

*Or* launch a server:

	> py -3 hello.py --servissimo
	
Make requests:

	requests.post("http://localhost:8080/api", data={"name": "Placissimo"})
	requests.post("http://localhost:8080/tasks").text
	""" Response: 
	{
		"servissimo_001": {
			"caller": "hello.py.main",
			"start_time": "2019-02-01T18:15:49.728341",
			"end_time": "2019-02-01T18:15:49.737351",
			"running": false,
			"done": true,
			"result": "Hello Placissimo",
			"exception": null
		}
	} """

Additional command line options let you:

- Render a default HTML file: `-index-file="placissimo/lib/index.html"`
- Choose a custom port: `-port=5000`
- Allow GET access: `-allow-get`
- Send and receive log statements with JavaScript:
  - Prohibit client sockets from sending messages to each other: `-websocket-mode=private`
  - Allow client sockets to "chat" with each other: `-websocket-mode=broadcast`
- References local files and folders: `-filesystem-path="." `
  - Parents and siblings of this folder aren't accessible.

To see the options do:

	> py -3 hello.py --servissimo -h

## If You're Still Interested ##
For more information, see `./docs/documentation.md`.
