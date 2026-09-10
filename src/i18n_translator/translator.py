"""Recursively translate the string leaves of a JSON-like structure."""
from __future__ import annotations

from typing import Any, Protocol


class SupportsTranslate(Protocol):
    """Anything with a ``translate(text, *, source_lang, target_lang)`` method."""

    def translate(self, text: str, *, source_lang: str, target_lang: str) -> str: ...


def translate_tree(
    value: Any,
    client: SupportsTranslate,
    *,
    source_lang: str,
    target_lang: str,
) -> Any:
    """Return a deep copy of ``value`` with every ``str`` leaf translated.

    Dict keys, numbers, booleans and ``None`` are kept as-is; only string values
    are sent to the client. The input object is never mutated.
    """
    if isinstance(value, str):
        return client.translate(value, source_lang=source_lang, target_lang=target_lang)
    if isinstance(value, dict):
        return {
            key: translate_tree(item, client, source_lang=source_lang, target_lang=target_lang)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            translate_tree(item, client, source_lang=source_lang, target_lang=target_lang)
            for item in value
        ]
    return value


def count_strings(value: Any) -> int:
    """Count translatable string leaves — used for progress reporting."""
    if isinstance(value, str):
        return 1
    if isinstance(value, dict):
        return sum(count_strings(item) for item in value.values())
    if isinstance(value, list):
        return sum(count_strings(item) for item in value)
    return 0
