.. naming documentation master file, created by
   sphinx-quickstart on Sun Feb 12 12:56:58 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. py-config::

    splashscreen:
        enabled: false
    packages:
    - matplotlib
    - naming

.. include:: ../../README.md
   :parser: myst_parser.sphinx_

.. py-editor::
    :config: pyscript.toml
    :env: index

    # definition
    import naming
    class NameFileConvention(naming.Name, naming.File):
        config = dict(first=r'\w+', last=r'\w+', number=r'\d+')

    # inspection
    name = NameFileConvention('john doe 07.jpg')
    print(f"{name.last=}")
    print(f"{name.number=}")

    # modification
    print(name.get(first='jane', number=99))  # returns new name string
    name.last = 'connor'  # mutates current name
    print(name)

    # validation
    try:
        name.number = 'not_a_number'
    except ValueError as exc:
        print(f"An error occurred: {exc}")

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    Overview
    Class List
    genindex
