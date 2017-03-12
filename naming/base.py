# standard
import re
import abc
import typing


def _regex_property(pattern_name: str) -> property:
    def getter(self):
        pattern = getattr(self, rf'__{pattern_name}')
        return rf'(?P<{pattern_name}>{pattern})'

    def setter(self, value):
        setattr(self, rf'__{pattern_name}', value)
    return property(getter, setter)


class _ABCName(abc.ABCMeta):
    def __new__(mcs, name, bases, args):
        new_cls = super().__new__(mcs, name, bases, args)
        mcs._merge_bases_dict('config', new_cls, bases)
        mcs._merge_bases_dict('compounds', new_cls, bases)
        new_cls._compounds_fields = set().union(*[v for v in new_cls.compounds.values()])
        mcs._merge_bases_drops(new_cls, bases)
        return new_cls

    @staticmethod
    def _merge_bases_dict(name, new_cls, bases):
        base_maps = [getattr(b, name, {}) for b in bases]
        base_maps.append(getattr(new_cls, name, {}))
        new_map = {}
        for dic in base_maps:
            new_map.update(dic)
        setattr(new_cls, name, new_map)

    @staticmethod
    def _merge_bases_drops(new_cls, bases):
        new_drops = set(getattr(new_cls, 'drops', tuple()))
        for b in bases:
            for drop in getattr(b, 'drops', tuple()):
                new_drops.add(drop)
                new_cls.config.pop(drop, None)
        new_cls.drops = new_drops


class _BaseName(object, metaclass=_ABCName):
    """This is the base abstract class for Name objects.
    All subclasses are encouraged to inherit from Name or EasyName instead of this one."""

    _regex_property_name = r'[a-zA-Z][\w]+'

    def __init__(self, name: str='', separator: str='_'):
        """Initialisation of the object sets the patterns defined by the _set_patterns method and
        calls _init_name_core. If any extra work is to be done by the class init it should be implemented on the
        _init_name_core method.

        :param name: Name to initialize the object with. Defaults to an empty string and it can later be set
                     by calling the :func:`~naming.Name.set_name` method.
        :param separator: Separator for the name fields. Defaults to an underscore.
        """
        super().__init__()
        self.__values = {}
        self.__items = self.__values.items()
        self._set_separator(separator)
        self._set_patterns()
        self._init_name_core(name)

    def _init_name_core(self, name: str):
        """Runs whenever a Name object is initialized or its name is set."""
        self.__set_name(name)
        self._set_values()
        self.__set_regex()
        self.__validate()

    def _set_separator(self, separator: str):
        self._separator = rf'{separator}'
        self._separator_pattern = rf'\{separator}'

    @property
    def separator(self) -> str:
        """The string that acts as a separator of all the fields in the name."""
        return self._separator

    @separator.setter
    def separator(self, value: str):
        """The string that acts as a separator of all the fields in the name."""
        self._set_separator(value)
        name = self.get_name(**self.get_values()) if self.name else None
        self._init_name_core(name)

    @abc.abstractmethod
    def _set_patterns(self):
        pass

    def _set_pattern(self, *patterns):
        for p in patterns:
            setattr(self.__class__, rf'_{p}', _regex_property(p))

    def __set_name(self, name: str):
        self.__name = rf'{name}' if name else None

    @property
    def name(self) -> str:
        """The name string set on the object."""
        return self.__name

    @abc.abstractmethod
    def _set_values(self):
        pass

    def __set_regex(self):
        self.__regex = re.compile(r'^{}$'.format(self._get_joined_pattern()))

    def __validate(self):
        if not self.name:
            return
        self.set_name(self.name)

    def set_name(self, name: str):
        """Set this object's name to the provided string.

        :param name: The name to be set on this object.
        :raises NameError: If an invalid string is provided.
        """
        match = self.__regex.match(name)
        if not match:
            msg = rf'Can not set invalid name "{name}".'
            raise NameError(msg)
        self.__set_name(name)
        self.__values.update(match.groupdict())

    @property
    # def _values(self) -> typing.Dict[str, str]:
    def _values(self) -> dict:
        return self.__values

    def __getattr__(self, attr):
        try:
            return self._values[attr]
        except KeyError:
            raise AttributeError(rf"{self.__class__} object has no attribute '{attr}'")

    @abc.abstractmethod
    def _get_pattern_list(self) -> typing.List[str]:
        return []

    def _get_values_pattern(self) -> typing.List[str]:
        return [getattr(self, p) for p in self._get_pattern_list()]

    def _get_joined_pattern(self) -> str:
        return self._separator_pattern.join(self._get_values_pattern())

    # def get_values(self) -> typing.Dict[str, str]:
    def get_values(self) -> dict:
        """Get the field values of this object's name as a dictionary in the form of {field: value}."""
        return {k: v for k, v in self.__items if not self._filter_kv(k, v)}

    def _filter_kv(self, k: str, v) -> bool:
        if self._filter_k(k) or self._filter_v(v):
            return True

    def _filter_k(self, k: str):
        pass

    def _filter_v(self, v):
        return v is None

    @property
    def nice_name(self) -> str:
        """This object's pure name attribute."""
        return self._get_nice_name()

    def _get_nice_name(self, **values) -> str:
        return self._separator.join(self._iter_translated_pattern_list('_get_pattern_list', **values))

    def get_name(self, **values) -> str:
        """Get a new name string from this object's name values.

        :param values: Variable keyword arguments where the **key** should refer to a field on this object that will
                       use the provided value to build the new name.
        """
        if not values and self.name:
            return self.name
        if values:
            for ck, cv in getattr(self, 'compounds', {}).items():
                if ck not in values:
                    compounds = []
                    for c in cv:
                        try:
                            value = values.get(c) or getattr(self, c)
                        except AttributeError:
                            break
                        compounds.append(rf'{value}')
                    else:
                        values[ck] = ''.join(compounds)
        return self._get_nice_name(**values)

    def _iter_translated_pattern_list(self, pattern: str, **values) -> typing.Generator:
        self_values = self._values
        for p in getattr(self, pattern)():
            nice_name = re.search(self._regex_property_name, p).group(0)
            if nice_name in values:
                value = str(values[nice_name])
            elif self_values:
                try:
                    value = str(self_values[nice_name])
                except KeyError:
                    value = getattr(self, p)  # must be a valid property
            else:
                value = rf'[{nice_name}]'
            yield value
