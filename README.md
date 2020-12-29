# naming
[![Build Status](https://travis-ci.org/chrizzFTD/naming.svg?branch=master)](https://travis-ci.org/chrizzFTD/naming)
[![Coverage Status](https://coveralls.io/repos/github/chrizzFTD/naming/badge.svg?branch=master)](https://coveralls.io/github/chrizzFTD/naming?branch=master)
[![Documentation Status](https://readthedocs.org/projects/naming/badge/?version=latest)](https://naming.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/naming.svg)](https://badge.fury.io/py/naming)
[![PyPI](https://img.shields.io/pypi/pyversions/naming.svg)](https://pypi.python.org/pypi/naming)

Object-oriented names for the digital era.

`naming` provides an interface for dealing with naming conventions; from
defining them, to identifying names and creating new ones.
    
### Installation

`naming` is available for Python 3.7 onwards via PyPI.

```bash
$ pip install naming
```

### Usage

Please refer to the [documentation](http://naming.readthedocs.io/en/latest/) for details on contents and usage.

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
>>> name.get(first='jane', number=99)  # returns new name string
'jane doe 99.jpg'
>>> name.last = 'connor'  # mutates current name
>>> name
NameFileConvention("john connor 07.jpg")
>>> name.number = 'not_a_number'
...
ValueError: Can't set field 'number' with invalid value 'not a number' on 'NameFileConvention("john doe 07.jpg")'. A valid field value should match pattern: '\d+'
```

