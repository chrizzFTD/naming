#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# naming documentation build configuration file, created by
# sphinx-quickstart on Mon Feb 13 22:13:36 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# namingpath = r'B:\write\code\git\naming'
# import sys
# sys.path.append(namingpath)
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.doctest',
              'sphinx.ext.intersphinx',
              'sphinx.ext.todo',
              'sphinx.ext.coverage',
              # 'sphinx.ext.imgmath',
              # 'sphinx.ext.ifconfig',
              'sphinx.ext.viewcode',
              # 'sphinx.ext.githubpages',
              'sphinx.ext.graphviz',
              'sphinx.ext.inheritance_diagram',
              'sphinx_autodoc_typehints']

# graphviz_dot = r'B:\__appdata__\graphviz\bin\dot.exe'
inheritance_graph_attrs = dict(bgcolor='transparent')

# inheritance_node_attrs = dict(shape='Mrecord', fontsize=14, height=0.75, color='dodgerblue1', style='filled')
inheritance_node_attrs = dict(shape='Mrecord', color='"#2573a7"', style='filled', fillcolor='"#eaf4fa"')

inheritance_edge_attrs = dict(color='"#123a54"')

autodoc_member_order = 'groupwise'
autodoc_default_flags = ['members', 'show-inheritance']


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'naming'
copyright = '2017, Christian López Barrón'
author = 'Christian López Barrón'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.1'
# The full version, including alpha/beta/rc tags.
release = '0.1.4'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'
# highlight_options = {'language': 'pycon'}
# highlight_language = 'pycon'
highlight_language = 'python3'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'nature'
# html_theme = 'pydoctheme'
html_theme = 'sphinx_rtd_theme'
# html_theme = 'classic'
# import sphinx_py3doc_enhanced_theme
# html_theme = "sphinx_py3doc_enhanced_theme"
# html_theme_path = [sphinx_py3doc_enhanced_theme.get_html_theme_path()]

# html_theme_options = {
#     # 'githuburl': 'https://github.com/ionelmc/sphinx-py3doc-enhanced-theme/',
#     'bodyfont': '"Lucida Grande",Arial,sans-serif',
#     'headfont': '"Lucida Grande",Arial,sans-serif',
#     'codefont': 'monospace,sans-serif',
#     'linkcolor': '#0072AA',
#     'visitedlinkcolor': '#6363bb',
#     'extrastyling': False,
# }
# pygments_style = 'friendly'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'namingdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'naming.tex', 'naming Documentation',
     'Christian López Barrón', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'naming', 'naming Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'naming', 'naming Documentation',
     author, 'naming', 'One line description of project.',
     'Miscellaneous'),
]




# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/3': None}
