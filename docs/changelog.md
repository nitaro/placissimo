# Changelog #

## Version 0.0.13 ##

  - Hashing websocket identifiers.
  - Minor documentation fixes.

## Version 0.0.12 ##

  - Added BaseHandler class.
  - Forcing tornado version < 6.0 to avoid decorator AttributeError per https://github.com/mher/flower/issues/878.
  - Websocket logger is now hashing websocket connection id's.
  - Now using pipenv.
  - Sorted imports with `isort -ds`
  - Formatted with `autopep8 . -ri`

## Version 0.0.11 ##

- Changed `/filesystem` response:
  - Changed field order.
  - Added `full_path` and `full_container` fields.
  - Now using default path separator instead of forcing forward slashes.

## Version 0.0.1 ##

- First version.