# -*- coding: utf-8 -*-
"""
The pipe module.
"""
# package
from .base import Name


class Pipe(Name):
    """docstring for Pipe"""
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
    def pipe_name(self):
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

    def get_name(self, **values):
        if not values and self.name:
            return super(Pipe, self).get_name(**values)
        try:
            # allow for getting name without pipe field in subclasses e.g. .File
            pipe = values['pipe'] or ''
        except KeyError:
            kwargs = {k: values.get(k) for k in self._pipe_fields}
            pipe = self._get_pipe_field(**kwargs)
        return rf'{super(Pipe, self).get_name(**values)}{pipe}'
