import os
import sys

# Добавление корневой директории пакета в sys.path
sys.path.insert(0, os.path.abspath(".."))

project = "structural-materials"
copyright = "2026, Aleksandr Ponomarev"
author = "Aleksandr Ponomarev"
release = "0.3.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "myst_parser",
    "sphinx_copybutton",
]

# Поддержка NumPy и Google docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Настройки autodoc
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Расширения файлов документации
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "ru"

# Тема оформления
html_theme = "furo"
html_title = "structural-materials"
html_static_path = ["_static"]

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}
