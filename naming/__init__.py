from pathlib import Path

from .base import _BaseName, NameConfig

__all__ = ['Name', 'File', 'Pipe', 'PipeFile', 'NameConfig']


class Name(_BaseName):
    """Inherited by: :class:`naming.File` :class:`naming.Pipe`

    Base class for name objects.

    Each subclass may have its own `config` attribute that should be a dictionary in the form of {field: pattern}
    where pattern is a valid regular expression.

    Classes may as well have a `drops` iterable attribute representing the fileds they want to ignore from their bases
    and a `compounds` dictionary attribute for nesting existing fields into new ones (or to override other fields).

    All fields should be unique. No duplicates are allowed.

    ======  ==========
    **Config:**
    ------------------
    *base*  Accepts any amount of word characters
    ======  ==========

    Basic use::

        >>> from naming import Name
        >>> n = Name()
        >>> n.get_name()  # no name has been set on the object, convention is solved with [missing] fields
        '{base}'
        >>> n.values
        {}
        >>> n.name = 'hello_world'
        >>> n.values
        {'base': 'hello_world'}
        >>> n.base = 'through_field_name'
        >>> n.values
        {'base': 'through_field_name'}
    """
    config = dict(base=r'\w+')


class File(Name):
    """Inherited by: :class:`naming.PipeFile`

    File Name objects.

    ========  ========
    **Unique Fields:**
    ------------------------
    *suffix*  Any amount of word characters
    ========  ========

    Basic use::

        >>> from naming import File
        >>> f = File()
        >>> f.get_name()
        '{basse}.{suffix}'
        >>> f.get_name(suffix='png')
        '{base}.png'
        >>> f.name = 'hello.world'
        >>> f.values
        {'base': 'hello', 'suffix': 'world'}
        >>> f.suffix
        'world'
        >>> f.suffix = 'abc'
        >>> f.name
        'hello.abc'
        >>> f.values
        {'base': 'hello', 'suffix': 'abc'}
        >>> f = File(cwd='some/path')
        >>> f.fullpath
        WindowsPath('some/path/{base}.{suffix}')
    """
    file_config = NameConfig(dict(suffix='\w+'))

    def __init__(self, *args, cwd=None, **kwargs):
        self.cwd = cwd
        super().__init__(*args, **kwargs)

    @property
    def _pattern(self) -> str:
        sep = '\.'
        casted = self.cast_config(self.file_config)
        pat = r'(\.{suffix})'.format(sep=sep, **casted)
        return rf'{super()._pattern}{pat}'

    def get_name(self, **values) -> str:
        if not values and self.name:
            return super().get_name()
        suffix = values.get('suffix') or self.suffix or '{suffix}'
        return rf'{super().get_name(**values)}.{suffix}'

    def get_path_pattern_list(self) -> list:
        """Fields / properties names (sorted) to concatenate and use when solving `path` and `fullpath` attributes"""
        return []

    @property
    def cwd(self) -> Path:
        """Path used as the current working directory when solving the `fullpath` attribute. Defaults to Path.home()"""
        return self._cwd

    @cwd.setter
    def cwd(self, value: str):
        self._cwd = Path(value or Path.home())

    @property
    def path(self) -> Path:
        """The Path representing this object on the filesystem."""
        args = list(self._iter_translated_field_names(self.get_path_pattern_list()))
        args.append(self.get_name())
        return Path(*args)

    @property
    def fullpath(self) -> Path:
        """The resolved full Path representing this object on the filesystem."""
        return Path.joinpath(self.cwd, self.path)


class Pipe(Name):
    """Inherited by: :class:`naming.PipeFile`

    Pipe Name objects.

    =========  =========
    **Unique Fields:**
    --------------------
    *output**  Any amount of word characters
    *version*  Any amount of digits
    *frame***  Any amount of digits
    \* optional field. ** exists only when *output* is there as well.
    ====================

    ======  ============
    **Composed Fields:**
    --------------------
    *pipe*  Combination of unique fields in the form of: (.{output})\*.{version}.{frame}**
    \* optional field. ** exists only when *output* is there as well.
    ====================

    Basic use::

        >>> from naming import Pipe
        >>> p = Pipe()
        >>> p.get_name()
        '{base}.{pipe}'
        >>> p.get_name(version=10)
        '{base}.10'
        >>> p.get_name(output='data')
        '{base}.data.{version}'
        >>> p.get_name(output='cache', version=7, frame=24)
        '{base}.cache.7.24'
        >>> p = Pipe('my_wip_data.1')
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
    """
    pipe_config = NameConfig(dict(pipe='\w+', output='\w+', version='\d+', frame='\d+'))

    @property
    def _pattern(self):
        sep = rf'\{self.pipe_separator}'
        casted = self.cast_config(self.pipe_config)
        pat = r'(?P<pipe>({sep}{output})?{sep}{version}({sep}{frame})?)'.format(sep=sep, **casted)
        return rf'{super()._pattern}{pat}'

    @property
    def pipe_separator(self) -> str:
        """The string that acts as a separator of the pipe fields."""
        return '.'

    @property
    def pipe_name(self) -> str:
        """The pipe name string of this object."""
        pipe_suffix = self.pipe or rf"{self.pipe_separator}{{pipe}}"
        return rf'{self.nice_name}{pipe_suffix}'

    def _format_pipe_field(self, k, v):
        if k == 'frame' and v is None:
            return ''
        return rf'{self.pipe_separator}{v if v is not None else rf"{{{k}}}"}'

    def _get_pipe_field(self, output=None, version=None, frame=None) -> str:
        fields = dict(output=output or None, version=version, frame=frame)
        # comparisons to None due to 0 being a valid value
        fields = {k: v if v is not None else self._values.get(k) for k, v in fields.items()}
        if all(v is None for v in fields.values()):
            suffix = rf'{self.pipe_separator}{{pipe}}'
            return self.pipe or suffix if self.name else suffix
        if not fields['output'] and fields['frame'] is None:  # optional fields
            return rf'{self.pipe_separator}{fields["version"]}'
        return ''.join(self._format_pipe_field(k, v) for k, v in fields.items())

    def get_name(self, **values) -> str:
        if not values and self.name:
            return super().get_name()
        try:
            # allow for getting name without pipe field in subclasses
            pipe = values['pipe'] or ''
        except KeyError:
            kwargs = {k: values.get(k) for k in self.pipe_config}
            kwargs.pop('pipe')
            pipe = self._get_pipe_field(**kwargs)
        return rf'{super().get_name(**values)}{pipe}'


class PipeFile(File, Pipe):
    """
    Basic use::

        >>> from naming import PipeFile
        >>> p = PipeFile('wipfile.7.ext')
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
        >>> class ProjectFile(PipeFile):
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
        'output': 'data',
        'version': '17',
        'suffix': 'abc'}
        >>> pf.nice_name  # no pipe & suffix fields
        'project_data_name_2017_christianl_constant_iamlast'
        >>> pf.year
        '2017'
        >>> pf.year = 'nondigits'  # mutating with invalid fields raises a NameError
        Traceback (most recent call last):
        ...
        NameError: Can't set invalid name 'project_data_name_nondigits_christianl_constant_iamlast.data.17.abc' on ProjectFile instance. Valid convention is: {base}_{year}_{user}_{another}_{last}.{pipe}.{suffix}
        >>> pf.year = 1907
        >>> pf.name
        'project_data_name_1907_christianl_constant_iamlast.data.17.abc'
        >>> pf.suffix
        'abc'
        >>> pf.separator = '  '  # you can set the separator to a different set of characters
        >>> pf.name
        'project_data_name  1907  christianl  constant  iamlast.data.17.abc'
    """
    pass
