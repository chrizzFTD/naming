# -*- coding: utf-8 -*-
"""
The file module.
"""
# standard
import os
from pathlib import Path
# package
from .pipe import Pipe

CWD = None


class File(Pipe):
    """docstring for File"""
    def _set_values(self):
        super(File, self)._set_values()
        self._extension = '[.](?P<extension>[a-zA-Z0-9]+)'

    def _get_joined_pattern(self):
        return '{}{}'.format(super(File, self)._get_joined_pattern(), self._extension)

    def get_name(self, **values):
        if not values and self.name:
            return super(File, self).get_name(**values)
        try:
            extension = values.get('extension') or self.extension or '[extension]'
        except AttributeError:
            extension = '[extension]'
        return '{}.{}'.format(super(File, self).get_name(**values), extension)

    def _get_path_pattern_list(self):
        return []

    @property
    def path(self):
        args = self._get_translated_pattern_list('_get_path_pattern_list')
        args.append(self.get_name())
        return Path(os.path.join(*args))

    @property
    def full_path(self):
        cwd = Path.home() if not CWD else CWD
        return Path.joinpath(cwd, self.path)
