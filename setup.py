#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='naming',
    version='0.1.1',
    packages=find_packages(),
    description='Object-oriented names for the digital era.',
    author='Christian López Barrón',
    author_email='chris.gfz@gmail.com',
    url='https://github.com/chrizzFTD/naming',
    download_url='https://github.com/chrizzFTD/naming/releases/tag/0.1.1',
    classifiers=['Programming Language :: Python :: 3.6'],
    extras_require={'docs': ['sphinx_autodoc_typehints']}
)
