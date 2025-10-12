.. py-config::

    splashscreen:
        enabled: false

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


**Name**

.. py-editor::
    :config: pyscript.toml

    from naming import Name
    class BasicName(Name):
        config = dict(base=r'\w+')

    n = BasicName()
    print(f"{n.get()=}")  # no name has been set on the object, convention is solved with {missing} fields
    print(f"{n.values=}")

    n.name = 'hello_world'
    print(f"{n=!r}")
    print(f"{str(n)=}")  # cast to string

    # modify name and get values from field names
    n.base = 'through_field_name'
    print(f"{n.values=}")
    print(f"{n.base=}")


**Pipe**

.. py-editor::
    :config: pyscript.toml

    from naming import Pipe
    class BasicPipe(Pipe):
        config = dict(base=r'\w+')

    p = BasicPipe()
    print(f"{p.get()=}")
    print(f"{p.get(version=10)=}")
    print(f"{p.get(output='cache', version=7, index=24)=}")

    p = BasicPipe('my_wip_data.1')
    print(f"{p.values=}")
    p.output = 'exchange'  # mutates the object
    p.index = 101
    p.version = 7
    print(f"{p.name=}")
    print(f"{p.values=}")

**File**

.. py-editor::
    :config: pyscript.toml

    from naming import File
    class BasicFile(File):
        config = dict(base=r'\w+')

    f = BasicFile()
    print(f"{f.get()=}")
    print(f"{f.get(suffix='png')=}")

    f = BasicFile('hello.world')
    print(f"{f.values=}")
    f.suffix = 'abc'
    print(f"{f.path=}")

**PipeFile**

.. py-editor::
    :config: pyscript.toml

    from naming import PipeFile
    class BasicPipeFile(PipeFile):
        config = dict(base=r'\w+')

    p = BasicPipeFile('wipfile.7.ext')
    print(f"{p.values=}")
    for idx in range(10):
        print(p.get(index=idx, output='render'))


.. topic:: Extending Names

    The **config**, **drop** and **join** attributes are merged on subclasses.

    Inheriting from an existing name::

        >>> class ProjectFile(BasicPipeFile):
        ...     config = dict(year='[0-9]{4}',
        ...                   user='[a-z]+',
        ...                   another='(constant)',
        ...                   last='[a-zA-Z0-9]+')
        ...
        >>> pf = ProjectFile('project_data_name_2017_christianl_constant_iamlast.data.17.abc', sep='_')
        >>> pf.values
        {'base': 'project_data_name',
        'year': '2017',
        'user': 'christianl',
        'another': 'constant',
        'last': 'iamlast',
        'pipe': '.data.17',
        'output': 'data',
        'version': '17',
        'suffix': 'abc'}
        >>> pf.nice_name  # no pipe & suffix fields
        'project_data_name_2017_christianl_constant_iamlast'
        >>> pf.year
        '2017'
        >>> pf.year = 'nondigits'  # mutating with invalid fields raises a ValueError
        Traceback (most recent call last):
        ...
        ValueError: Can't set field 'year' with invalid value 'nondigits' on 'ProjectFile("project_data_name_2017_christianl_constant_iamlast.data.17.abc")'. A valid field value should match pattern: '[0-9]{4}'
        >>> pf.year = 1907
        >>> pf
        ProjectFile("project_data_name_1907_christianl_constant_iamlast.data.17.abc")
        >>> pf.suffix
        'abc'
        >>> pf.sep = '  '  # you can set the separator to a different set of characters
        >>> pf.name
        'project_data_name   1907   christianl   constant   iamlast.data.17.abc'

    Dropping fields from bases::

        >>> class Dropper(BasicPipeFile):
        ...     config = dict(without=r'[a-zA-Z0-9]+', basename=r'[a-zA-Z0-9]+')
        ...     drop=('base',)
        ...
        >>> d = Dropper()
        >>> d.get()
        '{without}_{basename}.{pipe}.{suffix}'
        >>> # New subclasses will drop the 'base' field as well
        >>> Subdropper = type('Dropper', (Dropper,), dict(config=dict(subdrop='[\w]')))
        >>> s = Subdropper()
        >>> s.get()
        '{without}_{basename}_{subdrop}.{pipe}.{suffix}'

    Setting compound fields::

        >>> # splitting the 'base' field into multiple joined fields
        >>> class Compound(BasicPipeFile):
        ...     config=dict(first=r'\d+', second=r'[a-zA-Z]+')
        ...     join=dict(base=('first', 'second'))
        ...
        >>> c = Compound()
        >>> c.get()  # we see the original field 'base'
        '{base}.{pipe}.{suffix}'
        >>> c.get(first=50, second='abc')  # providing each field to join will work
        '50abc.{pipe}.{suffix}'
        >>> c.name = c.get(base='101dalmatians', version=1, suffix='png')  # providing the key field will also work
        >>> c.nice_name
        '101dalmatians'
        >>> c.get(first=200)
        '200dalmatians.1.png'
        >>> class CompoundByDash(Compound):
        ...     join_sep = '-'  # you can specify the string to join compounds
        ...
        >>> c = CompoundByDash('101-dalmatians.1.png')
        >>> c.get(first=300)
        '300-dalmatians.1.png'

    Defining path rules for File subclasses::

        >>> from naming import File
        >>> class FilePath(File):
        ...     config = dict(base=r'\w+', extrafield='[a-z0-9]+')
        ...     def get_path_pattern_list(self):
        ...         # As an example we are returning the pattern list from the name object (base, extrafield)
        ...         return super().get_pattern_list()
        ...
        >>> fp = FilePath()
        >>> fp.get()
        '{base} {extrafield}.{suffix}'
        >>> # path attribute will vary depending on the OS
        >>> fp.path
        WindowsPath('{base}/{extrafield}/{base} {extrafield}.{suffix}')

    Using properties as fields while solving names::

        >>> from naming import PipeFile
        >>> class PropertyField(PipeFile):
        ...     config = dict(base=r'\w+', extrafield='[a-z0-9]+')
        ...
        ...     @property
        ...     def nameproperty(self):
        ...         return 'staticvalue'
        ...
        ...     @property
        ...     def pathproperty(self):
        ...         return 'path_field'
        ...
        ...     def get_path_pattern_list(self):
        ...         result = super().get_pattern_list()
        ...         result.append('pathproperty')
        ...         return result
        ...
        ...     def get_pattern_list(self):
        ...         result = super().get_pattern_list()
        ...         result.append('nameproperty')
        ...         return result
        ...
        >>> pf = PropertyField()
        >>> pf.get()
        '{base} {extrafield} staticvalue.{pipe}.{suffix}'
        >>> pf.name = 'simple props staticvalue.1.abc'
        >>> pf.values
        {'base': 'simple',
        'extrafield': 'props',
        'nameproperty': 'staticvalue',
        'pipe': '.1',
        'version': '1',
        'suffix': 'abc'}
        >>> pf.path
        WindowsPath('simple/props/path_field/simple props staticvalue.1.abc')
