import os
import sys

project = "OCDS Metrics Analysis"

master_doc = "index"

# Make sure ReadTheDocs can see our classes
sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
]

html_theme = "sphinx_rtd_theme"
