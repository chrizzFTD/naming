import re
import typing
from collections import ChainMap
from types import MappingProxyType


def dct_from_mro(cls, attr_name):
    # TODO: replace with collections.ChainMap on py37+ (not now because 3.6 does not respect order)
    d = {}
    for mapping in filter(None, (getattr(c, attr_name, None) for c in reversed(cls.mro()))):
        d.update(mapping)
    return d


def _sorted_items(dct):
    """Given a mapping where values are iterables, iterate over the values whose contained references are not used as
    keys first:

    Example:
        >>> dct = {'two': ('two', 'one', 'foo'), 'one': ('hi', 'six', 'net'), 'six': ('three', 'four'), 'foo': ['bar']}
        >>> for k, v in _sorted_items(dct):
        ...     print(k, v)
        ...
        six ('three', 'four')
        foo ['bar']
        one ('hi', 'six', 'net')
        two ('two', 'one', 'foo')
    """
    to_solve = set(dct)
    while to_solve:
        for ck, cvs in dct.items():
            if ck not in to_solve or (to_solve - {ck}).intersection(cvs):  # other fields left to solve before this one
                continue
            yield ck, cvs
            to_solve.remove(ck)


class NameConfig:
    def __init__(self, cfg=None, name=None):
        if not isinstance(cfg, MappingProxyType):
            cfg = MappingProxyType(cfg or {})
        self.cfg = cfg
        self.name = name
        self.memcache = {}

    def __get__(self, obj, objtype):
        cfg = self.cfg
        if obj is None:
            return cfg
        # configs are immutable, so can cache here
        result = self.memcache.get(self.name)
        if self.name and isinstance(result, MappingProxyType):
            return result

        result = {}
        cmps = {k: v for k, v in objtype.compounds.items() if k in cfg}
        cmps_fields = set().union(*(v for v in cmps.values()))

        # solve compound fields
        solved = dict()
        for ck, cvs in _sorted_items(cmps):
            solved[ck] = ''.join(obj.cast(solved.pop(cv, cfg[cv]), cv, cv != ck) for cv in cvs)

        for k, v in cfg.items():
            if k in cmps and k in solved:  # a compound may be nested. ensure it's also in the solved dict
                result[k] = solved[k]
            elif k in cmps_fields:
                continue
            else:
                result[k] = v

        result = MappingProxyType(result)
        self.memcache[self.name] = result
        return result

    def __set__(self, obj, val):
        raise AttributeError("Can't set read-only attribute")

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name


class FieldValue:
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype):
        return obj._values.get(self.name)

    def __set__(self, obj, val):
        if val and str(val) == obj._values.get(self.name):
            return
        new_name = obj.get_name(**{self.name: val})
        obj.name = new_name


class _BaseName:
    """This is the base abstract class for Name objects. You should not need to subclass directly from this object.
    All subclasses are encouraged to inherit from Name instead of this one."""

    config = dict()
    compounds = dict()
    drops = tuple()

    def __init_subclass__(cls, **kwargs):
        cls.drops = set().union(*(getattr(c, 'drops', tuple()) for c in cls.mro()))
        cls.compounds = MappingProxyType(dct_from_mro(cls, 'compounds'))

        cfg = dct_from_mro(cls, 'config')
        for drop in cls.drops:
            cfg.pop(drop, None)
            setattr(cls, drop, None)

        for k in ChainMap(cfg, *(nc.cfg for nc in vars(cls).values() if isinstance(nc, NameConfig))):
            setattr(cls, k, FieldValue(k))

        cls.config = NameConfig(MappingProxyType(cfg), 'config')

    def __init__(self, name: str = '', sep: str = ' '):
        super().__init__()
        self._values = {}
        self._items = self._values.items()
        self._set_separator(sep)
        self._init_name_core(name)

    def _init_name_core(self, name: str):
        """Runs whenever a Name object is initialized or its name is set."""
        self._name = rf'{name}' if name else ''
        self.__set_regex()
        self.__validate()

    def _set_separator(self, separator: str):
        self._separator = rf'{separator}'
        self._separator_pattern = rf'\{separator}'

    @property
    def sep(self) -> str:
        """The string that acts as a separator of all the fields in the name."""
        return self._separator

    @sep.setter
    def sep(self, value: str):
        self._set_separator(value)
        name = self.get_name(**self.values) if self.name else None
        self._init_name_core(name)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        """Set this object's name to the provided string.

        :param name: The name to be set on this object.
        :raises NameError: If an invalid string is provided.
        """
        match = self.__regex.match(name)
        if not match:
            msg = (rf"Can't set invalid name '{name}' on {self.__class__.__name__} instance. "
                   rf"Valid convention is: '{self.__class__().get_name()}' with pattern: {self._pattern}'")
            raise NameError(msg)

        self._name = rf'{name}'
        self._values.update(match.groupdict())

    def __set_regex(self):
        self.__regex = re.compile(rf'^{self._pattern}$')

    @property
    def _pattern(self) -> str:
        casted = (self.cast(self.config.get(p, getattr(self, p)), p) for p in self.get_pattern_list())
        return self._separator_pattern.join(casted)

    def __validate(self):
        if not self._name:
            return
        self.name = self._name

    def get_pattern_list(self) -> typing.List[str]:
        return list(self.config)

    @property
    def values(self) -> dict:
        """The field values of this object's name as a dictionary in the form of {field: value}."""
        return {k: v for k, v in self._items if v is not None}

    @property
    def nice_name(self) -> str:
        """This object's pure name attribute."""
        return self._get_nice_name()

    def _get_nice_name(self, **values) -> str:
        return self._separator.join(self._iter_translated_field_names(self.get_pattern_list(), **values))

    def get_name(self, **values) -> str:
        """Get a new name string from this object's name values.

        :param values: Variable keyword arguments where the **key** should refer to a field on this object that will
                       use the provided value to build the new name.
        """
        if not values and self.name:
            return self.name
        if values:
            # if values are provided, solve compounds that may be affected
            for ck, cvs in _sorted_items(self.compounds):
                if ck in cvs and ck in values:  # redefined compound name to outer scope e.g. fifth = (fifth, sixth)
                    continue
                comp_values = [values.pop(cv, getattr(self, cv)) for cv in cvs]
                if None not in comp_values:
                    values[ck] = ''.join(rf'{v}' for v in comp_values)
        return self._get_nice_name(**values)

    def _iter_translated_field_names(self, pattern: typing.Iterable[str], **values) -> typing.Generator:
        for field_name in pattern:
            if field_name in values:
                yield rf'{values[field_name]}'
            else:
                yield getattr(self, field_name) or rf'{{{field_name}}}'

    @staticmethod
    def cast(value, name, named=True):
        return rf'(?P<{name}>{value})' if named else rf'{value}'

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        name = self.name or ''
        return rf'{self.__class__.__name__}("{name}")'
