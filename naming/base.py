import re
import typing
from itertools import chain
from collections import ChainMap
from types import MappingProxyType


def _dct_from_mro(cls: type, attr_name: str) -> dict:
    """"Get a merged dictionary from `cls` bases attribute `attr_name`. MRO defines importance (closest = strongest)."""
    d = {}
    for c in reversed(cls.mro()):
        d.update(getattr(c, attr_name, {}))
    return d


def _sorted_items(mapping: typing.Mapping) -> typing.Generator:
    """Given a mapping where values are iterables, yield items whose values contained references are not used as
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
    to_yield = set(mapping)
    while to_yield:
        for key, values in mapping.items():
            if key not in to_yield or (to_yield - {key} & set(values)):  # other keys left to yield before this one
                continue
            yield key, values
            to_yield.remove(key)


class NameConfig:
    def __init__(self, cfg: typing.Mapping = None, name: str = None):
        if not isinstance(cfg, MappingProxyType):
            cfg = MappingProxyType(cfg or {})
        self.cfg = cfg
        self.name = name
        self.memo = {}

    def __get__(self, obj, objtype):
        cfg = self.cfg
        if obj is None:
            return cfg
        # configs are immutable, so can cache here
        result = self.memo.get(self.name) or {}
        if self.name and isinstance(result, MappingProxyType):
            return result

        # don't solve compound fields that are not related to the current config
        compounds = {k: v for k, v in objtype.join.items() if (k in cfg or set(v).intersection(cfg))}
        solved = dict()  # will not preserve order
        pattern_lookup = ChainMap({}, solved, cfg)
        for ck, cvs in _sorted_items(compounds):
            # cast the compound values to regex groups, named unless a value is equal to the current key `ck`
            # search first in `cfg`, then in the object for properties
            compound_fields = {cv: obj.cast(solved.pop(cv, pattern_lookup.get(cv, getattr(obj, cv))), cv if cv != ck else '') for cv in cvs}
            compound_pattern = obj.join_sep.join(compound_fields.values())
            compound_fields[ck] = solved[ck] = compound_pattern
            pattern_lookup.update(compound_fields)

        compounds_fields = set().union(*(v for v in compounds.values()))
        for k, v in cfg.items():
            if k in compounds and k in solved:  # a compound may be nested. ensure it's also in the solved dict
                result[k] = solved.pop(k)
            elif k in compounds_fields:
                continue
            else:
                result[k] = v

        # keep track of solved compounds that were not referenced by `cfg`
        obj._uc = MappingProxyType(pattern_lookup)
        objtype._uc = obj._uc

        result = MappingProxyType(result)
        self.memo[self.name] = result
        return result

    def __set__(self, obj, val):
        msg = f"Can't set read-only attribute '{self.name}' to '{val}' on instance: {obj!r}."
        raise AttributeError(msg)

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name


class FieldValue:
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype):
        if obj is None:
            return
        return obj._values.get(self.name)

    def __set__(self, obj, val):
        if val and str(val) == obj._values.get(self.name):
            return
        new_name = obj.get(**{self.name: val})
        try:
            obj.name = new_name
        except ValueError:
            if self.name in obj.config:
                pattern = obj.config[self.name]
                msg = (rf"Can't set field '{self.name}' with invalid value '{val}' on '{obj!r}'. "
                       rf"A valid field value should match pattern: '{pattern}'")
                raise ValueError(msg)
            else:
                raise


class _BaseName:
    """This is the base abstract class for Name objects. You should not need to create instances of this class."""
    config = dict()
    drop = tuple()
    join = dict()
    join_sep = ''

    def __init_subclass__(cls, **kwargs):
        cls.join = MappingProxyType(_dct_from_mro(cls, 'join'))
        cls.drop = frozenset(chain.from_iterable(getattr(c, 'drop', tuple()) for c in cls.mro()))

        cfg = _dct_from_mro(cls, 'config')
        for drop in cls.drop:
            cfg.pop(drop, None)
            setattr(cls, drop, None)

        # fields in compounds and name config descriptors have to be accessible through their name on instances.
        configs = (nc.cfg for nc in vars(cls).values() if isinstance(nc, NameConfig))
        for k in set().union(cfg, cls.join, *configs):
            setattr(cls, k, FieldValue(k))

        cls.config = NameConfig(cfg, 'config')

    def __init__(self, name: str = '', sep: str = ' '):
        super().__init__()
        self._name = ''
        self._values = {}
        self._items = self._values.items()
        self._set_separator(sep)
        self._init_name_core(name)

    def _init_name_core(self, name: str):
        """Runs whenever a new instance is initialized or `sep` is set."""
        self.__regex = re.compile(rf'^{self._pattern}$')
        self.name = name

    def _set_separator(self, value: str):
        self._separator = rf'{value}' if value else ''
        self._separator_pattern = re.escape(self._separator)

    @property
    def sep(self) -> str:
        """The string that acts as a separator of all the fields in the name."""
        return self._separator

    @sep.setter
    def sep(self, value: str):
        self._set_separator(value)
        name = self.get(**self.values) if self.name else None
        self._init_name_core(name)

    @property
    def name(self) -> str:
        """This object's solved name.

        :raises ValueError: If an invalid string is provided when setting the attribute.
        """
        return self._name

    @name.setter
    def name(self, name: str):
        name = rf'{name}' if name else ''
        if name:
            match = self.__regex.match(name)
            if not match:
                proxy = self.__class__(sep=self._separator)
                pat = self.__regex.pattern
                msg = (rf"Can't set invalid name '{name}' on {self!r}. "
                       rf"Valid convention is: '{proxy.get()}' with pattern: '{pat}'")
                raise ValueError(msg)
            self._values.update(match.groupdict())
        else:
            self._values.clear()
        self._name = name

    @property
    def _pattern(self) -> str:
        pattern_list = self.get_pattern_list()
        if not pattern_list or not isinstance(pattern_list, (list, tuple)):
            msg = ('Expected list / tuple containing strings with field names from `get_pattern_list`. '
                   'Got: {} instead'.format(pattern_list))
            raise ValueError(msg)

        cfg = self.config
        casted = (self.cast(self._uc.get(p, getattr(self, p)), p) for p in self.get_pattern_list())
        return self._separator_pattern.join(casted)

    def get_pattern_list(self) -> typing.List[str]:
        """Fields / properties names (sorted) to be used when building names. Defaults to the keys of self.config"""
        return list(self.config)

    @property
    def values(self) -> typing.Dict[str, str]:
        """The field values of this object's name as a dictionary in the form of {field: value}."""
        return {k: v for k, v in self._items if v is not None}

    @property
    def nice_name(self) -> str:
        """This object's pure name without fields not present in `self.config`."""
        return self._get_nice_name()

    def _get_nice_name(self, **values) -> str:
        return self._separator.join(self._iter_translated_field_names(self.get_pattern_list(), **values))

    def get(self, **values) -> str:
        """Get a new name string from this object's name values.

        :param values: Variable keyword arguments where the **key** should refer to a field on this object that will
                       use the provided **value** to build the new name.
        """
        if not values and self.name:
            # no overridden field values to set, can return existing name string
            return self.name
        if values:
            # if values are provided, solve compounds that may be affected
            for ck, cvs in _sorted_items(self.join):
                if ck in cvs and ck in values:  # redefined compound name to outer scope e.g. fifth = (fifth, sixth)
                    continue
                if values.get(ck):
                    # compound key has been provided in values
                    continue
                comp_values = [values.pop(cv, getattr(self, cv)) for cv in cvs]
                if None not in comp_values:
                    # only if the full compound values are complete, we join and use it
                    values[ck] = self.join_sep.join(rf'{v}' for v in comp_values)
        return self._get_nice_name(**values)

    def _iter_translated_field_names(self, names: typing.Iterable[str], **values) -> typing.Generator:
        return (rf'{values[n]}' if n in values else getattr(self, n) or rf'{{{n}}}' for n in names)

    @staticmethod
    def cast(value: str, name: str = '') -> str:
        """Cast `value` to a grouped regular expression when `name` is provided."""
        return rf'(?P<{name}>{value})' if name else rf'{value}'

    @classmethod
    def cast_config(cls, config: typing.Mapping[str, str]) -> typing.Dict[str, str]:
        """Cast `config` to grouped regular expressions."""
        return {k: cls.cast(v, k) for k, v in config.items()}

    def __str__(self):
        return self.get()

    def __repr__(self):
        return rf'{self.__class__.__name__}("{self.name}")'
