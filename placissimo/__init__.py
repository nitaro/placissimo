import os as __os
from placissimo.__main__ import call
from placissimo.lib.server import serve

# set global module metadata.
__NAME__ = "Placissimo"
__DESCRIPTION__ = "Placissimo is a Plac intensifier."
__AUTHOR__ = "Nitin Arora"
__URL__ = "https://github.com/nitaro/placissimo"
__VERSION__ = "0.0.1"

# make ./lib/index.html importable.
index_file = __os.path.join(__os.path.dirname(__file__), "lib", "index.html")
