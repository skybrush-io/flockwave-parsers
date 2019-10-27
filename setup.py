"""Setup script for the Flockwave parsers package."""

from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages

requires = []

__version__ = None
exec(open("src/flockwave/parsers/version.py").read())

setup(
    name="flockwave-parsers",
    version=__version__,
    author=u"Tam\u00e1s Nepusz",
    author_email="tamas@collmot.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requires,
    extras_require={},
    test_suite="test",
)
