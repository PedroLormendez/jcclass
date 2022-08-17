# Configuration file for the Sphinx documentation builder.

# -- Project information

import sys 
import os

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../jcclass'))

vfile = {}
exec(open('../../jcclass/version,py').read(), vfile)

project = 'JCclass'
copyright = '2022, Pedro'
author = 'Pedro Herrera Lormendez'

release = vfile['__version']

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'