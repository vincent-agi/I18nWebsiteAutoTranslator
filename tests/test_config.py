import json

import pytest

from i18n_translator.config import ENV_VAR, resolve_api_key
from i18n_translator.errors import ConfigError


def test_cli_value_wins(monkeypatch, tmp_path):
    monkeypatch.setenv(ENV_VAR, "from-env")
    assert resolve_api_key("  from-cli  ", tmp_path / "nope.json") == "from-cli"


def test_env_var_used(monkeypatch, tmp_path):
    monkeypatch.setenv(ENV_VAR, "from-env")
    assert resolve_api_key(None, tmp_path / "nope.json") == "from-env"


def test_key_file_used(monkeypatch, tmp_path):
    monkeypatch.delenv(ENV_VAR, raising=False)
    path = tmp_path / "deepl-key.json"
    path.write_text(json.dumps({"deepl-key": "from-file"}), encoding="utf-8")
    assert resolve_api_key(None, path) == "from-file"


def test_missing_key_raises(monkeypatch, tmp_path):
    monkeypatch.delenv(ENV_VAR, raising=False)
    with pytest.raises(ConfigError):
        resolve_api_key(None, tmp_path / "absent.json")


def test_malformed_key_file_raises(monkeypatch, tmp_path):
    monkeypatch.delenv(ENV_VAR, raising=False)
    path = tmp_path / "deepl-key.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError):
        resolve_api_key(None, path)


def test_key_file_without_field_raises(monkeypatch, tmp_path):
    monkeypatch.delenv(ENV_VAR, raising=False)
    path = tmp_path / "deepl-key.json"
    path.write_text(json.dumps({"other": "x"}), encoding="utf-8")
    with pytest.raises(ConfigError):
        resolve_api_key(None, path)
