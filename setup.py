from placissimo import (__AUTHOR__, __DESCRIPTION__, __NAME__, __URL__,
                        __VERSION__)
from setuptools import setup, setuptools

doc = "README.md"


def read_doc():
    with open(doc) as d:
        return d.read()


setup(
    name=__NAME__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    doc=__DESCRIPTION__,
    url=__URL__,
    version=__VERSION__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.5",
    license="LICENSE.txt",
    long_description=read_doc(),
)
