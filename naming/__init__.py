# standard
from pathlib import Path
# package
from .base import _BaseName

__all__ = ['Name', 'File', 'Pipe', 'PipeFile']


CWD = None


class Name(_BaseName):
    """Inherited by: :class:`naming.File` :class:`naming.Pipe`

    Base class for name objects.

    Each subclass may have its own `config` attribute that should be a dictionary in the form of {field: pattern}
    where pattern is a valid regular expression.

    Classes may as well have a `drops` iterable attribute representing the fileds they want to ignore from their bases
    and a `compounds` dictionary attribute for nesting existing fields into multiple new ones.

    All fields should be unique. No duplicates are allowed.

    ======  ==========
    **Config:**
    ------------------
    *base*  Accepts any amount of word characters
    ======  ==========

    Basic use::

        >>> from naming import Name
        >>> n = Name()
        >>> n.get_name()
        '[base]'
        >>> n.get_values()
        {}
        >>> n.set_name('hello_world')
        >>> n.get_values()
        {'base': 'hello_world'}
        >>> n.base = 'fields_as_properties'
        >>> n.get_values()
        {'base': 'fields_as_properties'}
    """
    config = dict(base=r'[\w]+')
    drops = tuple()
    compounds = dict()

    def __init__(self, name: str='', separator: str='_'):
        """Sets the patterns defined by the `config` attribute. If any extra work is to be done by the class init
        it should be implemented on the `_init_name_core` method.

        :param name: Name to initialize the object with. Defaults to an empty string and it can later be set
                     by calling the :func:`~naming.Name.set_name` method.
        :param separator: Separator for the name fields. Defaults to an underscore.
        """
        self.__keys = self.config.keys()
        self.__items = self.config.items()
        super().__init__(name, separator)

    def _set_values(self):
        super()._set_values()
        for k, v in self.__items:
            setattr(self, rf'_{k}', v)
        for ck, cv in self.compounds.items():
            setattr(self, rf'_{ck}', ''.join(getattr(self, rf'_{v}') for v in cv))

    def _set_patterns(self):
        super()._set_patterns()
        self._set_pattern(*self.__keys)

    def get_pattern_list(self):
        result = super().get_pattern_list()
        result.extend(rf'_{k}' for k in self.__keys if not (k in self.drops or k in self._compounds_fields))
        return result


class File(Name):
    """Inherited by: :class:`naming.PipeFile`

    File Name objects.

    ===========  ===========
    **Unique Fields:**
    ------------------------
    *extension*  Any amount of characters in the class [a-zA-Z0-9]
    ===========  ===========

    Basic use::

        >>> from naming import File
        >>> f = File()
        >>> f.get_name()
        '[basse].[extension]'
        >>> f.get_name(extension='png')
        '[base].png'
        >>> f.set_name('hello.world')
        >>> f.get_values()
        {'base': 'hello', 'extension': 'world'}
        >>> f.extension
        'world'
        >>> f.extension = 'abc'
        >>> f.name
        'hello.abc'
        >>> f.get_values()
        {'base': 'hello', 'extension': 'abc'}
    """
    def __init__(self, *args, **kwargs):
        self._cwd = kwargs.pop('cwd', None)
        super().__init__(*args, **kwargs)

    def _set_values(self):
        super()._set_values()
        self._extension = '[.](?P<extension>[a-zA-Z0-9]+)'
        self._add_field_property('extension')

    def _get_joined_pattern(self) -> str:
        return rf'{super()._get_joined_pattern()}{self._extension}'

    def get_name(self, **values) -> str:
        if not values and self.name:
            return super().get_name(**values)
        extension = values.get('extension') or self.extension or "[extension]"
        return rf'{super().get_name(**values)}.{extension}'

    def get_path_pattern_list(self):
        return []

    @property
    def cwd(self):
        return self._cwd

    @cwd.setter
    def cwd(self, value):
        self._cwd = value

    @property
    def path(self) -> Path:
        """The Path representing this object on the filesystem."""
        args = list(self._iter_translated_pattern_list('get_path_pattern_list'))
        args.append(self.get_name())
        return Path(*args)

    @property
    def full_path(self) -> Path:
        """The resolved full Path representing this object on the filesystem."""
        cwd = Path.home() if not self.cwd else Path(self.cwd)
        return Path.joinpath(cwd, self.path)


class Pipe(Name):
    """Inherited by: :class:`naming.PipeFile`

    Pipe Name objects.

    =========  =========
    **Unique Fields:**
    --------------------
    *output**  Any amount of characters in the class [a-zA-Z0-9]
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
        '[base].[pipe]'
        >>> p.get_name(version=10)
        '[base].10'
        >>> p.get_name(output='data')
        '[base].data.[version]'
        >>> p.get_name(output='cache', version=7, frame=24)
        '[base].cache.7.24'
        >>> p = Pipe('my_wip_data.1')
        >>> p.version
        '1'
        >>> p.get_values()
        {'base': 'my_wip_data', 'version': '1'}
        >>> p.get_name(output='exchange')  # returns a new string name
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
        >>> p.get_values()
        {'base': 'my_wip_data', 'output': 'exchange', 'version': '7', 'frame': '101'}
    """
    _pipe_fields = ('output', 'version', 'frame')

    def _set_values(self):
        super()._set_values()
        self._version = '\d+'
        self._output = '[a-zA-Z0-9]+'
        self._frame = '\d+'
        self._pipe = rf'(({self._pipe_separator_pattern}{self._output})?[.]{self._version}([.]{self._frame})?)'

    def _set_patterns(self):
        super()._set_patterns()
        self._set_pattern('pipe', *self._pipe_fields)

    def _get_joined_pattern(self):
        return rf'{super()._get_joined_pattern()}{self._pipe}'

    @property
    def pipe_separator(self) -> str:
        return '.'

    @property
    def _pipe_separator_pattern(self):
        return rf'\{self.pipe_separator}'

    @property
    def pipe_name(self) -> str:
        """The pipe name string of this object."""
        pipe_suffix = self.pipe or rf"{self.pipe_separator}[pipe]"
        return rf'{self.nice_name}{pipe_suffix}'

    def _filter_k(self, k):
        return k == 'pipe'

    def _format_pipe_field(self, k, v):
        if k == 'frame' and v is None:
            return ''
        return rf'{self.pipe_separator}{v if v is not None else rf"[{k}]"}'

    def _get_pipe_field(self, output=None, version=None, frame=None) -> str:
        fields = dict(output=output or None, version=version, frame=frame)
        # comparisons to None due to 0 being a valid value
        fields = {k: v if v is not None else getattr(self, k) for k, v in fields.items()}

        if all(v is None for v in fields.values()):
            suffix = rf'{self.pipe_separator}[pipe]'
            return self.pipe or suffix if self.name else suffix

        if not fields['output'] and fields['frame'] is None:  # optional fields
            return rf'.{fields["version"] or 0}'

        return ''.join(self._format_pipe_field(k, v) for k, v in fields.items())

    def get_name(self, **values) -> str:
        if not values and self.name:
            return super().get_name(**values)
        try:
            # allow for getting name without pipe field in subclasses e.g. .File
            pipe = values['pipe'] or ''
        except KeyError:
            kwargs = {k: values.get(k) for k in self._pipe_fields}
            pipe = self._get_pipe_field(**kwargs)
        return rf'{super().get_name(**values)}{pipe}'


class PipeFile(File, Pipe):
    """
    Basic use::

        >>> from naming import PipeFile
        >>> p = PipeFile('wipfile.7.ext')
        >>> p.get_values()
        {'base': 'wipfile', 'version': '7', 'extension': 'ext'}
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
        >>> extra_fields = dict(year='[0-9]{4}', user='[a-z]+', another='(constant)', last='[a-zA-Z0-9]+')
        >>> ProjectFile = type('ProjectFile', (PipeFile,), dict(config=extra_fields))
        >>> pf = ProjectFile('project_data_name_2017_christianl_constant_iamlast_base.17.abc')
        >>> pf.get_values()
        {'base': 'project_data_name',
        'year': '2017',
        'user': 'christianl',
        'another': 'constant',
        'last': 'iamlast',
        'output': 'base',
        'version': '17',
        'extension': 'abc'}
        >>> pf.nice_name
        'project_data_name_2017_christianl_constant_iamlast'
        >>> pf.year
        '2017'
        >>> pf.lastfield
        'iamlast'
        >>> pf.extension
        'abc'
    """
    pass
