# -*- coding: utf-8 -*-
import os
import sys
import datetime

# Sphinx needs to be able to import the package to use autodoc and get the
# version number
sys.path.append(os.path.pardir)

from modelling_earth._version import get_versions

full_version = get_versions()["version"]


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

# intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "pandas": ("http://pandas.pydata.org/pandas-docs/stable/", None),
    "xarray": ("http://xarray.pydata.org/en/stable/", None),
    "matplotlib": ("https://matplotlib.org/", None),
}

# Autosummary pages will be generated by sphinx-autogen instead of sphinx-build
autosummary_generate = False

# Sphinx project configuration
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']
source_suffix = '.rst'
# The encoding of source files.
source_encoding = 'utf-8-sig'
master_doc = 'index'

# General information about the project
project = "Modelling Earth"
author = "Agustina Pesce"
if len(full_version.split('+')) > 1 or full_version == 'unknown':
    version = 'dev'
else:
    version = full_version


# Html configuration
html_last_updated_fmt = '%b %d, %Y'
html_title = project
html_short_title = project
html_static_path = ['_static']
html_extra_path = []
pygments_style = 'default'
add_function_parentheses = False
html_show_sourcelink = False
html_show_sphinx = True
html_show_copyright = True


# Theme config
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    'logo_only': True,
    'display_version': True,
}
html_context = {
    'menu_links_name': 'Useful links',
    'menu_links': [
        ('<i class="fa fa-github fa-fw"></i> Source Code', 'https://github.com/aguspesce/modelling_earth'),
    ],
    # Custom variables to enable "Improve this page"" and "Download notebook"
    # links
    'doc_path': 'doc',
    # 'galleries': sphinx_gallery_conf['gallery_dirs'],
    # 'gallery_dir': dict(zip(sphinx_gallery_conf['gallery_dirs'],
    #                         sphinx_gallery_conf['examples_dirs'])),
    'github_repo': 'aguspesce/modelling_earth',
    'github_version': 'master',
}
