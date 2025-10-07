# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Get project root (one level up from docs)
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from ebm.__version__ import version

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "EBM - Energibruksmodell"
copyright = "2025, The Norwegian Water Resources and Energy Directorate (NVE)"  # noqa: A001
author = "The Norwegian Water Resources and Energy Directorate (NVE)"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosectionlabel",
    "sphinx_tabs.tabs",
]

templates_path = ["_templates"]
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = [
    'custom.css',
]

html_css_files = [
    'css/custom.css',
]

#html_theme_options = {
#    "show_navbar_depth": 1,
#}

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

suppress_warnings = ['autosectionlabel.*']

# Konfigurasjon for Napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = False
add_module_names = False
modindex_common_prefix = ["src."]



# Use switch `-t internal` when building to include internal
# Load environment variables for substitution
ebm_installation_host = os.environ.get("EBM_INSTALLATION_HOST", os.environ.get('COMPUTERNAME', '??'))
# Make it available to templates

substitutions_rst = Path(__file__).parent / '_substitutions.rst'

substitutions = substitutions_rst.read_text(encoding='utf-8')


host_ = f"""
.. |ebm_installation_host| replace:: {ebm_installation_host}
"""

rst_epilog = substitutions + host_
