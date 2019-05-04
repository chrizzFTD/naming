#!/usr/bin/env python
from setuptools import setup, find_packages


_VERSION = '0.2.1'
setup(
    name='naming',
    version=_VERSION,
    packages=find_packages(
        exclude=("*.tests", "*.tests.*", "tests.*", "tests", "*.docs", "*.docs.*", "docs.*", "docs")),
    description='Object-oriented names for the digital era.',
    author='Christian López Barrón',
    author_email='chris.gfz@gmail.com',
    url='https://github.com/chrizzFTD/naming',
    download_url=f'https://github.com/chrizzFTD/naming/releases/tag/{_VERSION}',
    classifiers=['Programming Language :: Python :: 3.6'],
    extras_require={'docs': ['sphinx_autodoc_typehints', 'sphinx_rtd_theme']}
)
