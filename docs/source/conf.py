# Configuration file for the Sphinx documentation builder.

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information


import sys
import os

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../jcclass'))

vfile = {}
exec(open('../../jcclass/version.py').read(), vfile)

project = 'jcclass'
copyright = '2022, Pedro Herrera-Lormendez'
author = 'Pedro Herrera Lormendez'

release = vfile['__version__']

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
]

autosummary_generate = True
templates_path = ['_templates']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
#intersphinx_disabled_domains = ['std']



# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {

    # Set the name of the project to appear in the navigation.
    'nav_title': 'JCclass',
    'display_version': True,

    # Set you GA account ID to enable tracking
    #'google_analytics_account': 'XXX',

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://github.com/PedroLormendez/jcclass',
    'theme_color': 'green-grey',
    'color_primary': 'green-grey',
    'color_accent': 'white',
    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/PedroLormendez/jcclass',
    'repo_name': 'JCclass',
    'repo_type': 'github',
    }

# -- Options for EPUB output
epub_show_urls = 'footnote'
