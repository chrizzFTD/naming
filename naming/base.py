# standard
import re
import abc
import typing


def __regex_pattern(pattern_name: str) -> typing.Dict[str, typing.Callable]:
    def getter(self):
        pattern = getattr(self, rf'__{pattern_name}')
        return rf'(?P<{pattern_name}>{pattern})'

    def setter(self, value):
        setattr(self, rf'__{pattern_name}', value)
    return {'fget': getter, 'fset': setter}


class _AbstractBase(object):
    __metaclass__ = abc.ABCMeta
    """This is the base abstract class for Name objects.
    All subclasses are encouraged to inherit from Name or EasyName instead of this one."""

    def __init__(self, name: str='', separator: str='_'):
        """Initialisation of the object sets the patterns defined by the _set_patterns method and
        calls _init_name_core. If any extra work is to be done by the class init it should be implemented on the
        _init_name_core method.

        :param name: Name to initialize the object with. Defaults to an empty string and it can later be set
                     by calling the :func:`~naming.Name.set_name` method.
        :param separator: Separator for the name fields. Defaults to an underscore.
        """
        super(_AbstractBase, self).__init__()
        self.__values = {}
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
            string = rf"self.__class__._{p} = property(**__regex_pattern('{p}'))"  # please fix this hack
            exec(string)

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
        except (KeyError, TypeError):
            raise AttributeError("{} object has no attribute '{}'".format(self.__class__, attr))

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
        return {k: v for k, v in self._values.items() if not self._filter_kv(k, v)}

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
        return self._separator.join(self._get_translated_pattern_list('_get_pattern_list', **values))

    def get_name(self, **values) -> str:
        """Get a new name string from this object's name values.

        :param values: Variable keyword arguments where the **key** should refer to a field on this object that will
                       use the provided value to build the new name.
        """
        if not values and self.name:
            return self.name
        return self._get_nice_name(**values)

    def _get_translated_pattern_list(self, pattern: str, **values) -> typing.List[str]:
        self_values = self._values
        _values = []
        for p in getattr(self, pattern)():
            nice_name = p.replace('_', '')
            if nice_name in values:
                _values.append(str(values[nice_name]))
            elif self_values:
                try:
                    value = str(self_values[nice_name])
                except KeyError:
                    value = getattr(self, p)  # must be a valid property
                _values.append(value)
            else:
                _values.append(rf'[{nice_name}]')
        return _values
