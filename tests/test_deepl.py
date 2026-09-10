import pytest
import responses

from i18n_translator.deepl import FREE_ENDPOINT, PRO_ENDPOINT, DeepLClient, endpoint_for
from i18n_translator.errors import DeepLError

OK_BODY = {"translations": [{"text": "bonjour"}]}


def _add(body=OK_BODY, status=200):
    responses.add(responses.POST, FREE_ENDPOINT, json=body, status=status)


def test_empty_key_rejected():
    with pytest.raises(DeepLError):
        DeepLClient("")


def test_free_vs_pro_endpoint():
    assert endpoint_for("abc:fx") == FREE_ENDPOINT
    assert endpoint_for("abc") == PRO_ENDPOINT


@responses.activate
def test_translate_success(api_key):
    _add()
    client = DeepLClient(api_key, max_retries=1, backoff=0)
    assert client.translate("hello", source_lang="en", target_lang="fr") == "bonjour"


@responses.activate
def test_auth_header_sent(api_key):
    _add()
    DeepLClient(api_key, backoff=0).translate("hello", source_lang="en", target_lang="fr")
    assert responses.calls[0].request.headers["Authorization"] == f"DeepL-Auth-Key {api_key}"


@responses.activate
def test_client_error_returns_original_and_is_not_retried(api_key):
    _add(body={}, status=403)
    client = DeepLClient(api_key, max_retries=3, backoff=0)
    assert client.translate("hello", source_lang="en", target_lang="fr") == "hello"
    assert len(responses.calls) == 1


@responses.activate
def test_transient_error_is_retried_then_falls_back(api_key):
    for _ in range(3):
        _add(body={}, status=503)
    client = DeepLClient(api_key, max_retries=3, backoff=0)
    assert client.translate("hello", source_lang="en", target_lang="fr") == "hello"
    assert len(responses.calls) == 3


@responses.activate
def test_transient_then_success(api_key):
    _add(body={}, status=429)
    _add(OK_BODY, status=200)
    client = DeepLClient(api_key, max_retries=3, backoff=0)
    assert client.translate("hello", source_lang="en", target_lang="fr") == "bonjour"
    assert len(responses.calls) == 2


@responses.activate
def test_malformed_body_returns_original(api_key):
    _add({"unexpected": "shape"})
    client = DeepLClient(api_key, max_retries=1, backoff=0)
    assert client.translate("hello", source_lang="en", target_lang="fr") == "hello"


def test_blank_text_never_hits_network(api_key):
    # No responses.activate: a real HTTP call would raise ConnectionError.
    client = DeepLClient(api_key)
    assert client.translate("   ", source_lang="en", target_lang="fr") == "   "
    assert client.translate("", source_lang="en", target_lang="fr") == ""


@responses.activate
def test_context_manager_closes_session(api_key):
    _add()
    with DeepLClient(api_key, backoff=0) as client:
        client.translate("hello", source_lang="en", target_lang="fr")
