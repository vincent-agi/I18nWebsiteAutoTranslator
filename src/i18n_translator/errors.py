"""Exception hierarchy for i18n_translator."""
from __future__ import annotations


class I18nTranslatorError(Exception):
    """Base class for every error raised by this package."""


class ConfigError(I18nTranslatorError):
    """The DeepL API key could not be resolved."""


class DeepLError(I18nTranslatorError):
    """The DeepL API returned an unrecoverable error."""
