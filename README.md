# naming
[![Build Status](https://travis-ci.org/chrizzFTD/naming.svg?branch=master)](https://travis-ci.org/chrizzFTD/naming)
[![Coverage Status](https://coveralls.io/repos/github/chrizzFTD/naming/badge.svg?branch=master)](https://coveralls.io/github/chrizzFTD/naming?branch=master)
[![Documentation Status](https://readthedocs.org/projects/naming/badge/?version=latest)](https://naming.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/naming.svg)](https://badge.fury.io/py/naming)
[![PyPI](https://img.shields.io/pypi/pyversions/naming.svg)](https://pypi.python.org/pypi/naming)

Object-oriented names for the digital era.

naming provides a simple yet flexible and scalable interface for naming conventions.
It follows the UNIX tradition of single-purpose tools that do one thing well.

![Alt text](https://g.gravizo.com/source/svg/custom_mark10?https%3A%2F%2Fraw.githubusercontent.com%2FchrizzFTD%2Fnaming%2Ffeature%2Fgraphviz_readme%2FREADME.md)

<details> 
<summary></summary>
custom_mark10
digraph G {
    class -> format -> patterns  -> example;
    PIPE -> pipe_format -> pipe_patterns -> pipe_example;
    FILE -> file_format -> file_patterns -> file_example;
    PIPEFILE -> pipefile_format -> pipefile_patterns -> pipefile_example;
    PIPE -> PIPEFILE;
    FILE -> PIPEFILE;
}
custom_mark10
</details>
    
### Installation

naming is available for Python 3.6 onwards via PyPI.

```bash
$ pip install naming
```

### Usage

Refer to the [documentation](http://naming.readthedocs.io/en/latest/) for details on contents and usage.
