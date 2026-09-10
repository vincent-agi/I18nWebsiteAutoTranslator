"""i18n_translator — generate frontend i18n resource files via the DeepL API.

The package translates the *string values* of a JSON file while keeping the key
structure untouched, so a front-end can ship a ready-made resource bundle per
language instead of calling a translation API at runtime.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("i18n-translator")
except PackageNotFoundError:  # running from a source checkout without an install
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
