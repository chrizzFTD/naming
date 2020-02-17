# naming
[![Build Status](https://travis-ci.org/chrizzFTD/naming.svg?branch=master)](https://travis-ci.org/chrizzFTD/naming)
[![Coverage Status](https://coveralls.io/repos/github/chrizzFTD/naming/badge.svg?branch=master)](https://coveralls.io/github/chrizzFTD/naming?branch=master)
[![Documentation Status](https://readthedocs.org/projects/naming/badge/?version=latest)](https://naming.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/naming.svg)](https://badge.fury.io/py/naming)
[![PyPI](https://img.shields.io/pypi/pyversions/naming.svg)](https://pypi.python.org/pypi/naming)

Object-oriented names for the digital era.

naming provides a simple yet flexible and scalable interface for naming conventions.
It follows the UNIX tradition of single-purpose tools that do one thing well.

<div class="footer">
        <img src="https://docs.google.com/drawings/d/1wU-T04kgE7O_uVr4XRNIxGsnZP-TJmVxG5mqQE6mMNM/pub?w=1380&amp;h=980">
    </div>

![Alt text](https://g.gravizo.com/source/svg/custom_mark12?https%3A%2F%2Fraw.githubusercontent.com%2FchrizzFTD%2Fnaming%2Ffeature%2Fgraphviz_readme%2FREADME.mdnot)
<details> 
<summary></summary>
custom_mark12
  digraph G {
    size ="4,4";
    main [shape=box];
    main -> parse [weight=8];
    parse -> execute;
    main -> init [style=dotted];
    main -> cleanup;
    execute -> { make_string; printf};
    init -> make_string;
    edge [color=red];
    main -> printf [style=bold,label="100 times"];
    make_string [label="make a string"];
    node [shape=box,style=filled,color=".7 .3 1.0"];
    execute -> compare;
  }
custom_mark12
</details>
    
### Installation

naming is available for Python 3.6 onwards via PyPI.

```bash
$ pip install naming
```

### Usage

Refer to the [documentation](http://naming.readthedocs.io/en/latest/) for details on contents and usage.
