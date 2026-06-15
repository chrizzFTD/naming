Overview
========

.. topic:: Name Objects

    This package provides an interface for dealing with naming conventions; from defining them, to identifying names and creating new ones.

    Each Name object has a **config** attribute that contains the fields and regex patterns of the convention to follow.
    Names can also drop fields from their parent classes with the **drop** attribute, or they can merge / split fields with the **join** attribute.

Composition Example
===================
.. graphviz:: example.dot

Usage
=====

.. topic:: Built-ins & `config` attribute

    Inherit from the class to use and assign a class attribute `config` as a
    mapping of {field_name: regex_pattern} to use.

    The interactive REPL below defines ``BasicName``, ``BasicPipe``,
    ``BasicFile`` and ``BasicPipeFile``, runs the overview examples, and keeps
    the objects available at the prompt. Try changing ``n``, ``p``, ``f`` or
    ``pf`` after the examples finish running.

    .. raw:: html

        <py-repl
            repl-title="naming built-ins"
            theme="catppuccin-latte"
            packages="naming"
            src="_static/pyrepl/overview_builtins.py"
            no-banner>
        </py-repl>

.. topic:: Extending Names

    The **config**, **drop** and **join** attributes are merged on subclasses.

    This REPL defines and runs the subclassing, field dropping, compound field,
    path, and property-backed field examples. It leaves ``project_file``,
    ``dropper``, ``subdropper``, ``compound``, ``compound_by_dash``,
    ``file_path`` and ``property_field`` available for further experimentation.

    .. raw:: html

        <py-repl
            repl-title="naming extensions"
            theme="catppuccin-latte"
            packages="naming"
            src="_static/pyrepl/overview_extending.py"
            no-banner>
        </py-repl>
