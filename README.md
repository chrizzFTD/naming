# naming
[![Build Status](https://travis-ci.org/chrizzFTD/naming.svg?branch=master)](https://travis-ci.org/chrizzFTD/naming)
[![Coverage Status](https://coveralls.io/repos/github/chrizzFTD/naming/badge.svg?branch=master)](https://coveralls.io/github/chrizzFTD/naming?branch=master)
[![Documentation Status](https://readthedocs.org/projects/naming/badge/?version=latest)](https://naming.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/naming.svg)](https://badge.fury.io/py/naming)
[![PyPI](https://img.shields.io/pypi/pyversions/naming.svg)](https://pypi.python.org/pypi/naming)

Object-oriented names for the digital era.

naming provides a simple yet flexible and scalable interface for naming conventions.
It follows the UNIX tradition of single-purpose tools that do one thing well.
    
### Installation

naming is available for Python 3.6 onwards via PyPI.

```bash
$ pip install naming
```

### Usage

```python
>>> import naming
>>> class NameFileConvention(naming.Name, naming.File):
...     config = dict(first=r'\w+', last=r'\w+', number=r'\d+')
...
>>> name = NameFileConvention('john doe 07.jpg')
>>> name.last
'doe'
>>> name.number
'07'
>>> name.get_name(first='jane', number=99)
'jane doe 99.jpg'
>>> name.last = 'connor'
>>> name
NameFileConvention("john connor 07.jpg")
>>> name.number = 'not_a_number'
...
ValueError: Can't set invalid name 'john connor not_a_number.jpg' on NameFileConvention instance. Valid convention is: '{first} {last} {number}.{suffix}' with pattern: ^(?P<first>\w+)\ (?P<last>\w+)\ (?P<number>\d+)(\.(?P<suffix>\w+))$'
```

Refer to the [documentation](http://naming.readthedocs.io/en/latest/) for details on contents and usage.
