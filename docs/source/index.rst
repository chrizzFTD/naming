.. naming documentation master file, created by
   sphinx-quickstart on Sun Feb 12 12:56:58 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. py-config::

    splashscreen:
        enabled: false
    runtime: micropython
    packages:
    - naming

.. include:: ../../README.md
   :parser: myst_parser.sphinx_

.. py-editor::
   :config: pyscript_config.toml

   import naming
   class NameFileConvention(naming.Name, naming.File):
       config = dict(first=r'\w+', last=r'\w+', number=r'\d+')

   name = NameFileConvention('john doe 07.jpg')
   print(name.last)
   print(name.number)
   print(name.get(first='jane', number=99))  # returns new name string
   name.last = 'connor'  # mutates current name
   print(name)
   name.number = 'not_a_number'

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    Overview
    Class List
    genindex
