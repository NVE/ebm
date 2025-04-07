# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

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

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Konfigurasjon for Napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = False
add_module_names = False
modindex_common_prefix = ["src."]

