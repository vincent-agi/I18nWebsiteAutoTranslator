from i18n_translator.translator import count_strings, translate_tree


class FakeClient:
    """Records every text it is asked to translate and upper-cases it."""

    def __init__(self):
        self.seen = []

    def translate(self, text, *, source_lang, target_lang):
        self.seen.append(text)
        return text.upper()


def test_translates_only_string_leaves():
    client = FakeClient()
    data = {
        "title": "hello",
        "count": 3,
        "ratio": 1.5,
        "flag": True,
        "nothing": None,
        "nested": {"deep": ["a", "b"]},
        "items": [{"name": "x"}, {"name": "y"}],
    }
    result = translate_tree(data, client, source_lang="en", target_lang="fr")
    assert result == {
        "title": "HELLO",
        "count": 3,
        "ratio": 1.5,
        "flag": True,
        "nothing": None,
        "nested": {"deep": ["A", "B"]},
        "items": [{"name": "X"}, {"name": "Y"}],
    }
    assert sorted(client.seen) == ["a", "b", "hello", "x", "y"]


def test_input_is_not_mutated():
    client = FakeClient()
    data = {"a": ["x"], "b": {"c": "y"}}
    translate_tree(data, client, source_lang="en", target_lang="fr")
    assert data == {"a": ["x"], "b": {"c": "y"}}


def test_keys_are_never_translated():
    client = FakeClient()
    result = translate_tree({"greeting": "hi"}, client, source_lang="en", target_lang="fr")
    assert list(result) == ["greeting"]


def test_empty_containers():
    client = FakeClient()
    assert translate_tree({}, client, source_lang="en", target_lang="fr") == {}
    assert translate_tree([], client, source_lang="en", target_lang="fr") == []


def test_count_strings():
    assert count_strings({"a": "x", "b": [1, "y", {"c": "z"}], "d": 5}) == 3
    assert count_strings([]) == 0
    assert count_strings("solo") == 1
