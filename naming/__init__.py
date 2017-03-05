# standard
from pathlib import Path
# package
from .base import _BaseName

__all__ = ['Name', 'EasyName', 'File', 'Pipe', 'PipeFile']


CWD = None


class Name(_BaseName):
    """Inherited by: :class:`naming.EasyName` :class:`naming.File` :class:`naming.Pipe`

    Base class for name objects.

    ======  ==========
    **Unique Fields:**
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

    """
    def _set_values(self):
        super()._set_values()
        self._base = '[\w]+?'

    def _set_patterns(self):
        super()._set_patterns()
        self._set_pattern('base')

    def _get_pattern_list(self):
        super()._get_pattern_list()
        return ['_base']


class EasyName(Name):
    """Class that allows the easy creation of new Name objects.

    ========  ============
    **Unique attributes:**
    ----------------------
    *config*  Dictionary with the fields that will compose this name object.
    ========  ============

    Example::

        >>> from naming import EasyName, PipeFile
        >>> extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        >>> ProjectFile = type('ProjectFile', (EasyName, PipeFile), dict(config=extra_fields))
        >>> pf = ProjectFile('project_data_name_2017_christianl_constant_iamlast_base.17.abc')
        >>> pf.get_values()
        {'base': 'project_data_name',
        'year': '2017',
        'username': 'christianl',
        'anotherfield': 'constant',
        'lastfield': 'iamlast',
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
        >>> [pf.get_name(frame=x, output='render', year=2018) for x in range(10)]
        ['project_data_name_2018_christianl_constant_iamlast.render.17.0.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.1.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.2.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.3.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.4.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.5.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.6.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.7.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.8.abc',
        'project_data_name_2018_christianl_constant_iamlast.render.17.9.abc']

    """
    config = None

    def __init__(self, *args, **kwargs):
        if self.config is None:
            self.config = {}
        self.__keys = self.config.keys()
        self.__items = self.config.items()
        super().__init__(*args, **kwargs)

    def _set_values(self):
        super()._set_values()
        for k, v in self.__items:
            setattr(self, rf'_{k}', v)

    def _set_patterns(self):
        super()._set_patterns()
        for k in self.__keys:
            self._set_pattern(k)

    def _get_pattern_list(self):
        result = super()._get_pattern_list()
        result.extend(rf'_{k}' for k in self.__keys)
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

    """

    def _set_values(self):
        super()._set_values()
        self._extension = '[.](?P<extension>[a-zA-Z0-9]+)'

    def _get_joined_pattern(self) -> str:
        return rf'{super()._get_joined_pattern()}{self._extension}'

    def get_name(self, **values) -> str:
        if not values and self.name:
            return super().get_name(**values)
        try:
            extension = values.get('extension') or self.extension or '[extension]'
        except AttributeError:
            extension = '[extension]'
        return rf'{super().get_name(**values)}.{extension}'

    def _get_path_pattern_list(self):
        return []

    @property
    def path(self) -> Path:
        """The Path representing this object on the filesystem."""
        args = self._get_translated_pattern_list('_get_path_pattern_list')
        args.append(self.get_name())
        return Path(*args)

    @property
    def full_path(self) -> Path:
        """The resolved full Path representing this object on the filesystem."""
        cwd = Path.home() if not CWD else Path(CWD)
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
        try:
            return rf'{self.nice_name}{self.pipe}'
        except AttributeError:
            return rf'{self.nice_name}{self.pipe_separator}[pipe]'

    def _filter_k(self, k):
        return k == 'pipe'

    def _format_pipe_field(self, k, v):
        if k == 'frame' and v is None:
            return ''
        return rf'{self.pipe_separator}{v if v is not None else rf"[{k}]"}'

    def _get_pipe_field(self, output=None, version=None, frame=None) -> str:
        fields = dict(output=output or None, version=version, frame=frame)
        # comparisons to None due to 0 being a valid value
        fields = {k: v if v is not None else getattr(self, k, None) for k, v in fields.items()}

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

    """
    pass
