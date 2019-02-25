# Ideas For Later #
-----

## Definitely ##
- Add a unit test to make sure `dependency_error.DependencyError` is raised when `allow_websocket=True` but `index_file=None`.
- Add an option for secure cookie access.
- Add a Vue.js example.
	- The point of this would be to have an example with a filesystem browser.
	- This should include re-useable Vue snippets and should probably be a new repository called ~"placissimo-vue-snips".
	- If you can incorporate Node.js into this demo, that would be good.
- Add a Docker example.
	- This should be able to access the host's filesystem.

## Maybe ##
- Consider a `/cleanup` endpoint that accepts a task's thread name as a parameter and then removes the task from `@task_metadata`. If the task is still running this should return an error message.
	- Maybe this should also call `.shutdown()` for `ThreadPoolExecutor()`?
- Consider a `/cancel` endpoint that allows you to try and cancel a thread.
	- This would match the ability to stop a process from the command line with `Ctrl + C`.
- Consider adding an endpoint that uses the `inspect` module to provide information on the module function in question.
	- Ultimately, I don't think this is really a good idea because it's the users responsibility to create any required documentation for their application.
