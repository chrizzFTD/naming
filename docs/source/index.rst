.. naming documentation master file, created by
   sphinx-quickstart on Sun Feb 12 12:56:58 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. py-config::

    splashscreen:
        enabled: false
    runtime: micropython

.. include:: ../../README.md
   :parser: myst_parser.sphinx_

.. py-editor::

    print("hallo world")
    from pprint import pp
    pp(dir(1))

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    Overview
    Class List
    genindex
