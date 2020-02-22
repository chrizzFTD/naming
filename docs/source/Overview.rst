Overview
========

.. topic:: Name Objects

    This package offers classes representing names as strings that follow a certain pattern convention.
    Each Name object has a **config** attribute
    that contains the fields and regex patterns of the convention to follow. Names can also drop fields from their
    parent classes with the **drop** attribute, or they can merge / split fields with the **join** attribute.

Composition Example
===================
.. graphviz:: example.dot

Usage
=====

.. topic:: Built-ins & `config` attribute

    Inherit from the class to use and assign a class attribute `config` as a
    mapping of {field_name: regex_pattern} to use.

    Name::

        >>> from naming import Name
        >>> class BasicName(Name):
        ...     config = dict(base=r'\w+')
        ...
        >>> n = BasicName()
        >>> n.get_name()  # no name has been set on the object, convention is solved with {missing} fields
        '{base}'
        >>> n.values
        {}
        >>> n.name = 'hello_world'
        >>> n
        Name("hello_world")
        >>> str(n)  # cast to string
        'hello_world'
        >>> n.values
        {'base': 'hello_world'}
        >>> # modify name and get values from field names
        >>> n.base = 'through_field_name'
        >>> n.values
        {'base': 'through_field_name'}
        >>> n.base
        'through_field_name'

    Pipe::

        >>> from naming import Pipe
        >>> class BasicPipe(Pipe):
        ...     config = dict(base=r'\w+')
        ...
        >>> p = BasicPipe()
        >>> p.get_name()
        '{base}.{pipe}'
        >>> p.get_name(version=10)
        '{base}.10'
        >>> p.get_name(output='data')
        '{base}.data.{version}'
        >>> p.get_name(output='cache', version=7, frame=24)
        '{base}.cache.7.24'
        >>> p = BasicPipe('my_wip_data.1')
        >>> p.version
        '1'
        >>> p.values
        {'base': 'my_wip_data', 'pipe': '.1', 'version': '1'}
        >>> p.get_name(output='exchange')  # returns a new string
        'my_wip_data.exchange.1'
        >>> p.name
        'my_wip_data.1'
        >>> p.output = 'exchange'  # mutates the object
        >>> p.name
        'my_wip_data.exchange.1'
        >>> p.frame = 101
        >>> p.version = 7
        >>> p.name
        'my_wip_data.exchange.7.101'
        >>> p.values
        {'base': 'my_wip_data', 'pipe': '.exchange.7.101', 'output': 'exchange', 'version': '7', 'frame': '101'}

    File::

        >>> from naming import File
        >>> class BasicFile(File):
        ...     config = dict(base=r'\w+')
        ...
        >>> f = BasicFile()
        >>> f.get_name()
        '{basse}.{suffix}'
        >>> f.get_name(suffix='png')
        '{base}.png'
        >>> f = BasicFile('hello.world')
        >>> f.values
        {'base': 'hello', 'suffix': 'world'}
        >>> f.suffix
        'world'
        >>> f.suffix = 'abc'
        >>> f.name
        'hello.abc'
        >>> f.path
        WindowsPath('hello.abc')

    PipeFile::

        >>> from naming import PipeFile
        >>> class BasicPipeFile(PipeFile):
        ...     config = dict(base=r'\w+')
        ...
        >>> p = BasicPipeFile('wipfile.7.ext')
        >>> p.values
        {'base': 'wipfile', 'pipe': '.7', 'version': '7', 'suffix': 'ext'}
        >>> [p.get_name(frame=x, output='render') for x in range(10)]
        ['wipfile.render.7.0.ext',
        'wipfile.render.7.1.ext',
        'wipfile.render.7.2.ext',
        'wipfile.render.7.3.ext',
        'wipfile.render.7.4.ext',
        'wipfile.render.7.5.ext',
        'wipfile.render.7.6.ext',
        'wipfile.render.7.7.ext',
        'wipfile.render.7.8.ext',
        'wipfile.render.7.9.ext']

.. topic:: Extending Names

    The **config**, **drop** and **join** attributes are merged on the subclasses to provide a simple but flexible
    and scalable system that can help rule all names in a project.

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
        ValueError: Can't set invalid name 'project_data_name_nondigits_christianl_constant_iamlast.data.17.abc' on ProjectFile instance. Valid convention is: '{base}_{year}_{user}_{another}_{last}.{pipe}.{suffix}' with pattern: ^(?P<base>\w+)_(?P<year>[0-9]{4})_(?P<user>[a-z]+)_(?P<another>(constant))_(?P<last>[a-zA-Z0-9]+)(?P<pipe>(\.(?P<output>\w+))?\.(?P<version>\d+)(\.(?P<frame>\d+))?)(\.(?P<suffix>\w+))$'
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
        >>> d.get_name()
        '{without}_{basename}.{pipe}.{suffix}'
        >>> # New subclasses will drop the 'base' field as well
        >>> Subdropper = type('Dropper', (Dropper,), dict(config=dict(subdrop='[\w]')))
        >>> s = Subdropper()
        >>> s.get_name()
        '{without}_{basename}_{subdrop}.{pipe}.{suffix}'

    Setting compound fields::

        >>> # splitting the 'base' field into multiple joined fields
        >>> class Compound(BasicPipeFile):
        ...     config=dict(first=r'\d+', second=r'[a-zA-Z]+')
        ...     join=dict(base=('first', 'second'))
        ...
        >>> c = Compound()
        >>> c.get_name()  # we see the original field 'base'
        '{base}.{pipe}.{suffix}'
        >>> c.get_name(first=50, second='abc')  # providing each field to join will work
        '50abc.{pipe}.{suffix}'
        >>> c.name = c.get_name(base='101dalmatians', version=1, suffix='png')  # providing the key field will also work
        >>> c.nice_name
        '101dalmatians'
        >>> c.get_name(first=200)
        '200dalmatians.1.png'
        >>> class CompoundByDash(Compound):
        ...     join_sep = '-'  # you can specify the string to join compounds
        ...
        >>> c = CompoundByDash('101-dalmatians.1.png')
        >>> c.get_name(first=300)
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
        >>> fp.get_name()
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
        >>> pf.get_name()
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
