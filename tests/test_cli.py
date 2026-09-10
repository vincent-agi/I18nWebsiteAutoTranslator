import json

import responses

from i18n_translator.cli import main
from i18n_translator.deepl import FREE_ENDPOINT


@responses.activate
def test_end_to_end(tmp_path, monkeypatch):
    responses.add(
        responses.POST, FREE_ENDPOINT,
        json={"translations": [{"text": "translated"}]}, status=200,
    )
    src = tmp_path / "en.json"
    src.write_text(
        json.dumps({"a": "hello", "b": {"c": "world"}, "n": 1}), encoding="utf-8"
    )
    out = tmp_path / "nested" / "fr.json"
    monkeypatch.setenv("DEEPL_API_KEY", "k:fx")

    code = main(["-s", "en", "-t", "fr", "-i", str(src), "-o", str(out)])

    assert code == 0
    assert json.loads(out.read_text(encoding="utf-8")) == {
        "a": "translated",
        "b": {"c": "translated"},
        "n": 1,
    }


def test_missing_input_file_exits_1(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPL_API_KEY", "k:fx")
    code = main([
        "-s", "en", "-t", "fr",
        "-i", str(tmp_path / "nope.json"), "-o", str(tmp_path / "out.json"),
    ])
    assert code == 1


def test_invalid_json_exits_1(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPL_API_KEY", "k:fx")
    src = tmp_path / "bad.json"
    src.write_text("{oops", encoding="utf-8")
    code = main(["-s", "en", "-t", "fr", "-i", str(src), "-o", str(tmp_path / "out.json")])
    assert code == 1


def test_no_api_key_exits_1(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPL_API_KEY", raising=False)
    src = tmp_path / "en.json"
    src.write_text("{}", encoding="utf-8")
    code = main([
        "-s", "en", "-t", "fr", "-i", str(src), "-o", str(tmp_path / "out.json"),
        "--key-file", str(tmp_path / "absent.json"),
    ])
    assert code == 1


def test_credits_flag(capsys):
    assert main(["--credits"]) == 0
    assert "Vincent AGI" in capsys.readouterr().out
