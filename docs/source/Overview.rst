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

    Name

    .. py-repl::
       :packages: naming
       :repl-title: Name
       :no-banner:

       >>> from naming import Name
       >>> class BasicName(Name):
       ...     config = dict(base=r'\w+')
       ...
       >>> n = BasicName()
       >>> n.get()  # no name has been set on the object, convention is solved with {missing} fields
       >>> n.values
       >>> n.name = 'hello_world'
       >>> n
       >>> str(n)  # cast to string
       >>> n.values
       >>> # modify name and get values from field names
       >>> n.base = 'through_field_name'
       >>> n.values
       >>> n.base

    Pipe

    .. py-repl::
       :packages: naming
       :repl-title: Pipe
       :no-banner:

       >>> from naming import Pipe
       >>> class BasicPipe(Pipe):
       ...     config = dict(base=r'\w+')
       ...
       >>> p = BasicPipe()
       >>> p.get()
       >>> p.get(version=10)
       >>> p.get(output='data')
       >>> p.get(output='cache', version=7, index=24)
       >>> p = BasicPipe('my_wip_data.1')
       >>> p.version
       >>> p.values
       >>> p.get(output='exchange')  # returns a new string
       >>> p.name
       >>> p.output = 'exchange'  # mutates the object
       >>> p.name
       >>> p.index = 101
       >>> p.version = 7
       >>> p.name
       >>> p.values

    File

    .. py-repl::
       :packages: naming
       :repl-title: File
       :no-banner:

       >>> from naming import File
       >>> class BasicFile(File):
       ...     config = dict(base=r'\w+')
       ...
       >>> f = BasicFile()
       >>> f.get()
       >>> f.get(suffix='png')
       >>> f = BasicFile('hello.world')
       >>> f.values
       >>> f.suffix
       >>> f.suffix = 'abc'
       >>> f.name
       >>> f.path

    PipeFile

    .. py-repl::
       :packages: naming
       :repl-title: PipeFile
       :no-banner:

       >>> from naming import PipeFile
       >>> class BasicPipeFile(PipeFile):
       ...     config = dict(base=r'\w+')
       ...
       >>> p = BasicPipeFile('wipfile.7.ext')
       >>> p.values
       >>> [p.get(index=x, output='render') for x in range(10)]

.. topic:: Extending Names

    The **config**, **drop** and **join** attributes are merged on subclasses.

    Inheriting from an existing name

    .. py-repl::
       :packages: naming
       :src: _static/pyrepl_bootstrap.py
       :repl-title: Extending names
       :no-banner:

       >>> class ProjectFile(BasicPipeFile):
       ...     config = dict(year='[0-9]{4}',
       ...                   user='[a-z]+',
       ...                   another='(constant)',
       ...                   last='[a-zA-Z0-9]+')
       ...
       >>> pf = ProjectFile('project_data_name_2017_christianl_constant_iamlast.data.17.abc', sep='_')
       >>> pf.values
       >>> pf.nice_name  # no pipe & suffix fields
       >>> pf.year
       >>> pf.year = 'nondigits'  # mutating with invalid fields raises a ValueError
       >>> pf.year = 1907
       >>> pf
       >>> pf.suffix
       >>> pf.sep = '  '  # you can set the separator to a different set of characters
       >>> pf.name

    Dropping fields from bases

    .. py-repl::
       :packages: naming
       :src: _static/pyrepl_bootstrap.py
       :repl-title: Dropping fields
       :no-banner:

       >>> class Dropper(BasicPipeFile):
       ...     config = dict(without=r'[a-zA-Z0-9]+', basename=r'[a-zA-Z0-9]+')
       ...     drop=('base',)
       ...
       >>> d = Dropper()
       >>> d.get()
       >>> # New subclasses will drop the 'base' field as well
       >>> Subdropper = type('Dropper', (Dropper,), dict(config=dict(subdrop='[\w]')))
       >>> s = Subdropper()
       >>> s.get()

    Setting compound fields

    .. py-repl::
       :packages: naming
       :src: _static/pyrepl_bootstrap.py
       :repl-title: Compound fields
       :no-banner:

       >>> # splitting the 'base' field into multiple joined fields
       >>> class Compound(BasicPipeFile):
       ...     config=dict(first=r'\d+', second=r'[a-zA-Z]+')
       ...     join=dict(base=('first', 'second'))
       ...
       >>> c = Compound()
       >>> c.get()  # we see the original field 'base'
       >>> c.get(first=50, second='abc')  # providing each field to join will work
       >>> c.name = c.get(base='101dalmatians', version=1, suffix='png')  # providing the key field will also work
       >>> c.nice_name
       >>> c.get(first=200)
       >>> class CompoundByDash(Compound):
       ...     join_sep = '-'  # you can specify the string to join compounds
       ...
       >>> c = CompoundByDash('101-dalmatians.1.png')
       >>> c.get(first=300)

    Defining path rules for File subclasses

    In the browser REPL, paths appear as ``PosixPath``.

    .. py-repl::
       :packages: naming
       :repl-title: Path rules
       :no-banner:

       >>> from naming import File
       >>> class FilePath(File):
       ...     config = dict(base=r'\w+', extrafield='[a-z0-9]+')
       ...     def get_path_pattern_list(self):
       ...         # As an example we are returning the pattern list from the name object (base, extrafield)
       ...         return super().get_pattern_list()
       ...
       >>> fp = FilePath()
       >>> fp.get()
       >>> # path attribute will vary depending on the OS
       >>> fp.path

    Using properties as fields while solving names

    In the browser REPL, paths appear as ``PosixPath``.

    .. py-repl::
       :packages: naming
       :repl-title: Property fields
       :no-banner:

       >>> from naming import PipeFile
       >>> class PropertyField(PipeFile):
       ...     config = dict(base=r'\w+', extrafield='[a-z0-9]+')
       ...     @property
       ...     def nameproperty(self):
       ...         return 'staticvalue'
       ...     @property
       ...     def pathproperty(self):
       ...         return 'path_field'
       ...     def get_path_pattern_list(self):
       ...         result = super().get_pattern_list()
       ...         result.append('pathproperty')
       ...         return result
       ...     def get_pattern_list(self):
       ...         result = super().get_pattern_list()
       ...         result.append('nameproperty')
       ...         return result
       >>> pf = PropertyField()
       >>> pf.get()
       >>> pf.name = 'simple props staticvalue.1.abc'
       >>> pf.values
       >>> pf.path
