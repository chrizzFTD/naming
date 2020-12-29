import re
from pathlib import Path

from .base import _BaseName, NameConfig

__all__ = [
    'Name',
    'File',
    'Pipe',
    'PipeFile',
    'NameConfig',
]


class Name(_BaseName):
    """Base class for name objects.

    Each subclass may have its own `config` attribute that should be a dictionary in the form of {field: pattern}
    where `pattern` is a valid regular expression.

    Classes may as well have a `drop` iterable attribute representing the fileds they want to ignore from their bases
    and a `join` dictionary attribute for nesting existing fields into new ones (or to override other fields).

    All field names should be unique. No duplicates are allowed.

    Basic use::

        >>> from naming import Name
        >>> class MyName(Name):
        ...     config = dict(base=r'\w+')
        ...
        >>> n = MyName()
        >>> n.get()  # no name has been set on the object, convention is solved with {missing} fields
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
    """


class File(_BaseName):
    """Inherited by: :class:`naming.PipeFile`

    File Name objects.
    All named files are expected to have a suffix (extension) after a dot.

    ========  ========
    **Unique Fields:**
    ------------------------
    *suffix*  Any amount of word characters
    ========  ========

    Basic use::

        >>> from naming import File
        >>> class MyFile(File):
        ...     config = dict(base=r'\w+')
        ...
        >>> f = MyFile()
        >>> f.get()
        '{basse}.{suffix}'
        >>> f.get(suffix='png')
        '{base}.png'
        >>> f = MyFile('hello.world')
        >>> f.values
        {'base': 'hello', 'suffix': 'world'}
        >>> f.suffix
        'world'
        >>> f.suffix = 'abc'
        >>> f.name
        'hello.abc'
        >>> f.path
        WindowsPath('hello.abc')
    """
    file_config = NameConfig(dict(suffix='\w+'))

    @property
    def _pattern(self) -> str:
        sep = re.escape('.')
        casted = self.cast_config(self.file_config)
        pat = r'({sep}{suffix})'.format(sep=sep, **casted)
        return rf'{super()._pattern}{pat}'

    def get(self, **values) -> str:
        if not values and self.name:
            return super().get()
        suffix = values.get('suffix') or self.suffix or '{suffix}'
        return rf'{super().get(**values)}.{suffix}'

    def get_path_pattern_list(self) -> list:
        """Fields / properties names (sorted) to be used when solving `path`"""
        return []

    @property
    def path(self) -> Path:
        """A Path for this name object joining field names from `self.get_path_pattern_list` with this object's name"""
        args = list(self._iter_translated_field_names(self.get_path_pattern_list()))
        args.append(self.get())
        return Path(*args)


class Pipe(_BaseName):
    """Inherited by: :class:`naming.PipeFile`

    Pipe Name objects.
    The pipe composed field includes the specific pipeline elements unique to a resource,
    e.g.:
    version: Identifier that helps track important states of a pipeline resource during its lifecycle.
        This allows for history revision, rollback and comparisons.
        This field is always required.
    output: Optional field used when the produced data can be separated into meaningful distinct channels, e.g:
        left and right channel of a track. beauty, specular render passes. body, eyes, hair textures.
    index: Position of an element where the pipeline resource is a sequence.
        If an index is used, the output field must also exist. This is because otherwise
        distinguishing between an output and a version would become complex.
        E.g. a frame of a rendered scene. An UDIM tile of a texture. A chunk of a cache.


    =========  =========
    **Unique Fields:**
    --------------------
    *output**  Any amount of word characters
    *version*  Any amount of digits
    *index***  Any amount of digits
    \* optional field. ** exists only when *output* is there as well.
    ====================

    ======  ============
    **Composed Fields:**
    --------------------
    *pipe*  Combination of unique fields in the form of: (.{output})\*.{version}.{index}**
    \* optional field. ** exists only when *output* is there as well.
    ====================

    Basic use::

        >>> from naming import Pipe
        >>> class MyPipe(Pipe):
        ...     config = dict(base=r'\w+')
        ...
        >>> p = MyPipe()
        >>> p.get()
        '{base}.{pipe}'
        >>> p.get(version=10)
        '{base}.10'
        >>> p.get(output='data')
        '{base}.data.{version}'
        >>> p.get(output='cache', version=7, index=24)
        '{base}.cache.7.24'
        >>> p = MyPipe('my_wip_data.1')
        >>> p.version
        '1'
        >>> p.values
        {'base': 'my_wip_data', 'pipe': '.1', 'version': '1'}
        >>> p.get(output='exchange')  # returns a new string
        'my_wip_data.exchange.1'
        >>> p.name
        'my_wip_data.1'
        >>> p.output = 'exchange'  # mutates the object
        >>> p.name
        'my_wip_data.exchange.1'
        >>> p.index = 101
        >>> p.version = 7
        >>> p.name
        'my_wip_data.exchange.7.101'
        >>> p.values
        {'base': 'my_wip_data', 'pipe': '.exchange.7.101', 'output': 'exchange', 'version': '7', 'index': '101'}
    """
    pipe_config = NameConfig(dict(pipe='\w+', output='\w+', version='\d+', index='\d+'))

    @property
    def _pattern(self):
        sep = re.escape(self.pipe_sep)
        casted = self.cast_config(self.pipe_config)
        pat = r'(?P<pipe>({sep}{output})?{sep}{version}({sep}{index})?)'.format(sep=sep, **casted)
        return rf'{super()._pattern}{pat}'

    @property
    def pipe_sep(self) -> str:
        """The string that acts as a separator of the pipe fields."""
        return '.'

    @property
    def pipe_name(self) -> str:
        """The pipe name string of this object."""
        pipe_suffix = self.pipe or rf"{self.pipe_sep}{{pipe}}"
        return rf'{self.nice_name}{pipe_suffix}'

    def _format_pipe_field(self, k, v):
        if k == 'index' and v is None:
            return ''
        return rf'{self.pipe_sep}{v if v is not None else rf"{{{k}}}"}'

    def _get_pipe_field(self, output=None, version=None, index=None) -> str:
        fields = dict(output=output or None, version=version, index=index)
        # comparisons to None due to 0 being a valid value
        fields = {k: v if v is not None else self._values.get(k) for k, v in fields.items()}

        if all(v is None for v in fields.values()):
            suffix = rf'{self.pipe_sep}{{pipe}}'
            return self.pipe or suffix if self.name else suffix
        elif not fields['output'] and fields['index'] is None:  # optional fields
            return rf'{self.pipe_sep}{fields["version"]}'

        return ''.join(self._format_pipe_field(k, v) for k, v in fields.items())

    def get(self, **values) -> str:
        if not values and self.name:
            return super().get()
        try:
            # allow for getting name without pipe field in subclasses
            pipe = values['pipe'] or ''
        except KeyError:
            kwargs = {k: values.get(k) for k in self.pipe_config}
            kwargs.pop('pipe')
            pipe = self._get_pipe_field(**kwargs)
        return rf'{super().get(**values)}{pipe}'


class PipeFile(File, Pipe):
    """
    Basic use::

        >>> from naming import PipeFile
        >>> class MyPipeFile(PipeFile):
        ...     config = dict(base=r'\w+')
        ...
        >>> p = MyPipeFile('wipfile.7.ext')
        >>> p.values
        {'base': 'wipfile', 'pipe': '.7', 'version': '7', 'suffix': 'ext'}
        >>> [p.get(index=x, output='render') for x in range(10)]
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
        >>> class ProjectFile(MyPipeFile):
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
    """
