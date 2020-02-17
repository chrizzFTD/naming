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

![Alt text](http://g.gravizo.com/source/custom_mark?https%3A%2F%2Fraw.githubusercontent.com%2FchrizzFTD%2Fnaming%2Ffeature%2Fgraphviz_readme%2FREADME.md)
<details> 
<summary></summary>
custom_mark
strict digraph G {
    {
      node [style="rounded, filled" shape=box];
      class, FILE, PIPE, PIPEFILE;
    }
    {
      node [style=filled margin=0 width=1 height=0.46 shape=polygon fixedsize=true skew=0.4];
      format, file_format, pipe_format, pipefile_format;
    }
    {
      node [shape=none];
      patterns, file_patterns, pipe_patterns, pipefile_patterns;
    }
    {
      node [style="dashed, filled" shape=box];
      example, file_example, pipe_example, pipefile_example;
    }
    subgraph legend {
        edge[style=invis];
        class, format, example, patterns [color=gray40 fillcolor=gray95];
        patterns [label="field=pattern" fontcolor=gray22];
        class -> format -> patterns  -> example;
    }
    FILE, file_format, file_example [color=lightgoldenrod3 fillcolor=lemonchiffon1];
    file_format [label=".{suffix}"];
    file_example [label=".ext"];
    file_patterns [label="suffix = \w+" fontcolor=lightgoldenrod4];
    PIPE, pipe_format, pipe_example [color=lightskyblue4 fillcolor=lightblue];
    pipe_format [label=".{pipe}"];
    pipe_example [label=".1.out.101"];
    pipe_patterns [label="version = \d+ output=\w+? frame=\d+?"];
    PIPEFILE, pipefile_format, pipefile_example [color=mediumorchid4 fillcolor=plum2];
    pipefile_format [skew=0.15 width=2 label="{base}.{pipe}.{suffix}"];
    pipefile_example [label="framed_data.7.out.101.ext"];
    pipefile_patterns [label="base = \w+" fontcolor=mediumorchid4];
    edge [color=gray36 arrowhead="vee"];
    PIPE -> pipe_format -> pipe_patterns -> pipe_example;
    FILE -> file_format -> file_patterns -> file_example;
    PIPEFILE -> pipefile_format -> pipefile_patterns -> pipefile_example;
    {PIPE, FILE} -> PIPEFILE;
}
)
custom_mark
</details>
    
### Installation

naming is available for Python 3.6 onwards via PyPI.

```bash
$ pip install naming
```

### Usage

Refer to the [documentation](http://naming.readthedocs.io/en/latest/) for details on contents and usage.
