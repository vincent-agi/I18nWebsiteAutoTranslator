"""Resolve the DeepL API key from the CLI, the environment, or a local file."""
from __future__ import annotations

import json
import os
from pathlib import Path

from .errors import ConfigError

ENV_VAR = "DEEPL_API_KEY"
DEFAULT_KEY_FILE = "deepl-key.json"
KEY_FIELD = "deepl-key"


def resolve_api_key(
    cli_value: str | None = None,
    key_file: str | os.PathLike[str] | None = None,
) -> str:
    """Return the DeepL API key.

    Resolution order (first hit wins):

    1. ``cli_value`` — the ``--api-key`` option.
    2. the ``DEEPL_API_KEY`` environment variable.
    3. the ``deepl-key`` field of ``key_file`` (default: ``./deepl-key.json``).

    Raises:
        ConfigError: when no key can be found, or the key file is malformed.
    """
    if cli_value:
        return cli_value.strip()

    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return env_value.strip()

    path = Path(key_file or DEFAULT_KEY_FILE)
    if path.is_file():
        try:
            key = str(json.loads(path.read_text(encoding="utf-8"))[KEY_FIELD]).strip()
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ConfigError(f"{path} has no valid '{KEY_FIELD}' field") from exc
        if key:
            return key

    raise ConfigError(
        "No DeepL API key found. Set the DEEPL_API_KEY environment variable, "
        f"pass --api-key, or create {path} with a '{KEY_FIELD}' field."
    )
