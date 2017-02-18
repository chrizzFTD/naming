# standard
import os
from pathlib import Path
# package
from .base import _AbstractBase

__all__ = ['Name', 'EasyName', 'File', 'Pipe', 'PipeFile']


CWD = None


class Name(_AbstractBase):
    """Inherited by: :class:`naming.EasyName` :class:`naming.File` :class:`naming.Pipe`

    Base class for name objects.

    Contains only one field: *base* that accepts any word character.

    Basic use::

        >>> import naming
        >>> n = naming.Name()
        >>> n.get_name()
        '[base]'
        >>> n.get_values()
        {'base': None}

    """
    def _set_values(self):
        super(Name, self)._set_values()
        self._base = '[\w]+?'

    def _set_patterns(self):
        super(Name, self)._set_patterns()
        self._set_pattern('base')

    def _get_pattern_list(self):
        super(Name, self)._get_pattern_list()
        return ['_base']


class EasyName(Name):
    config = None

    def __init__(self, *args, **kwargs):
        if self.config is None:
            self.config = {}
        self.__keys = self.config.keys()
        self.__items = self.config.items()
        super(EasyName, self).__init__(*args, **kwargs)

    def _set_values(self):
        super(EasyName, self)._set_values()
        for k, v in self.__items:
            setattr(self, rf'_{k}', v)

    def _set_patterns(self):
        super(EasyName, self)._set_patterns()
        for k in self.__keys:
            self._set_pattern(k)

    def _get_pattern_list(self):
        result = super(EasyName, self)._get_pattern_list()
        result.extend([rf'_{k}' for k in self.__keys])
        return result


class File(Name):
    """Inherited by: :class:`naming.PipeFile`"""

    def _set_values(self):
        super(File, self)._set_values()
        self._extension = '[.](?P<extension>[a-zA-Z0-9]+)'

    def _get_joined_pattern(self) -> str:
        return rf'{super(File, self)._get_joined_pattern()}{self._extension}'

    def get_name(self, **values) -> str:
        """Get a new name string from this object's name values.

        :param values: Variable keyword arguments where the **key** should refer to a field on this object that will
                       use the provided value to build the new name. Fields unique to File objects: *extension*.
        """
        if not values and self.name:
            return super(File, self).get_name(**values)
        try:
            extension = values.get('extension') or self.extension or '[extension]'
        except AttributeError:
            extension = '[extension]'
        return rf'{super(File, self).get_name(**values)}.{extension}'

    def _get_path_pattern_list(self):
        return []

    @property
    def path(self) -> Path:
        """The Path representing this object on the filesystem."""
        args = self._get_translated_pattern_list('_get_path_pattern_list')
        args.append(self.get_name())
        return Path(os.path.join(*args))

    @property
    def full_path(self) -> Path:
        """The resolved full Path representing this object on the filesystem."""
        cwd = Path.home() if not CWD else Path(CWD)
        return Path.joinpath(cwd, self.path)


class Pipe(Name):
    """Inherited by: :class:`naming.PipeFile`"""
    _pipe_fields = ('output', 'version', 'frame')

    def _set_values(self):
        super(Pipe, self)._set_values()
        self._version = '\d+'
        self._output = '[a-zA-Z0-9]+'
        self._frame = '\d+'
        self._pipe = rf'(({self._separator_pattern}{self._output})?[.]{self._version}([.]{self._frame})?)'

    def _set_patterns(self):
        super(Pipe, self)._set_patterns()
        self._set_pattern('pipe', *self._pipe_fields)

    def _get_joined_pattern(self):
        return rf'{super(Pipe, self)._get_joined_pattern()}{self._pipe}'

    @property
    def pipe_name(self) -> str:
        """The pipe name string of this object."""
        try:
            return rf'{self.nice_name}{self.pipe}'
        except AttributeError:
            return rf'{self.nice_name}{self.separator}[pipe]'

    def _filter_k(self, k):
        return k == 'pipe'

    def _format_pipe_field(self, k, v):
        if k == 'frame' and v is None:
            return ''
        joiner = self.separator if k == 'output' else '.'
        return rf'{joiner}{v if v is not None else rf"[{k}]"}'

    def _get_pipe_field(self, version=None, output=None, frame=None) -> str:
        fields = dict(output=output, version=version, frame=frame)
        # comparisons to None due to 0 being a valid value
        fields = {k: v if v is not None else getattr(self, k, None) for k, v in fields.items()}

        if all(v is None for v in fields.values()):
            suffix = rf'{self.separator}[pipe]'
            return self.pipe or suffix if self.name else suffix

        if not fields['output'] and fields['frame'] is None:  # optional fields
            return rf'.{fields["version"]}'

        return ''.join([self._format_pipe_field(k, v) for k, v in fields.items()])

    def get_name(self, **values) -> str:
        """Get a new name string from this object's name values.

        :param values: Variable keyword arguments where the **key** should refer to a field on this object that will
                       use the provided value to build the new name. Fields unique to Pipe objects: *output*, *version*
                       and *frame*.
        """
        if not values and self.name:
            return super(Pipe, self).get_name(**values)
        try:
            # allow for getting name without pipe field in subclasses e.g. .File
            pipe = values['pipe'] or ''
        except KeyError:
            kwargs = {k: values.get(k) for k in self._pipe_fields}
            pipe = self._get_pipe_field(**kwargs)
        return rf'{super(Pipe, self).get_name(**values)}{pipe}'


class PipeFile(File, Pipe):
    pass
