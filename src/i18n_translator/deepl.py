"""Minimal DeepL REST API client."""
from __future__ import annotations

import logging
import time
from typing import Final

import requests

from .errors import DeepLError

_LOG = logging.getLogger(__name__)

FREE_ENDPOINT: Final = "https://api-free.deepl.com/v2/translate"
PRO_ENDPOINT: Final = "https://api.deepl.com/v2/translate"
_FREE_KEY_SUFFIX: Final = ":fx"


def endpoint_for(api_key: str) -> str:
    """Free-tier keys end with ``:fx``; every other key targets the Pro host."""
    return FREE_ENDPOINT if api_key.endswith(_FREE_KEY_SUFFIX) else PRO_ENDPOINT


class DeepLClient:
    """Thin wrapper around the DeepL ``/v2/translate`` endpoint.

    One :class:`requests.Session` is reused for every call so the underlying
    connection stays alive for a whole file. Transient errors (HTTP 429 and 5xx,
    network failures) are retried with a linear back-off; anything else — or a
    final give-up — returns the *original* text so a partial failure can never
    corrupt the output file.
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff: float = 1.0,
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise DeepLError("api_key must not be empty")
        self._endpoint = endpoint_for(api_key)
        self._timeout = timeout
        self._max_retries = max(1, max_retries)
        self._backoff = backoff
        self._session = session or requests.Session()
        self._session.headers.update({"Authorization": f"DeepL-Auth-Key {api_key}"})

    def translate(self, text: str, *, source_lang: str, target_lang: str) -> str:
        """Translate ``text`` and return the result, or ``text`` itself on failure."""
        if not text or text.isspace():
            return text

        payload = {
            "text": text,
            "source_lang": source_lang.upper(),
            "target_lang": target_lang.upper(),
        }

        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._session.post(self._endpoint, data=payload, timeout=self._timeout)
            except requests.RequestException as exc:
                _LOG.warning("DeepL request failed (%d/%d): %s", attempt, self._max_retries, exc)
                self._sleep(attempt)
                continue

            if response.status_code == 200:
                try:
                    return response.json()["translations"][0]["text"]
                except (ValueError, KeyError, IndexError):
                    _LOG.error("Unexpected DeepL body for %r: %s", _clip(text), _clip(response.text))
                    return text

            if response.status_code == 429 or response.status_code >= 500:
                _LOG.warning(
                    "DeepL transient error %d (%d/%d)",
                    response.status_code, attempt, self._max_retries,
                )
                self._sleep(attempt)
                continue

            _LOG.error("DeepL error %d for %r: %s", response.status_code, _clip(text), _clip(response.text))
            return text

        _LOG.error("DeepL gave up after %d attempt(s) for %r", self._max_retries, _clip(text))
        return text

    def _sleep(self, attempt: int) -> None:
        if self._backoff > 0 and attempt < self._max_retries:
            time.sleep(self._backoff * attempt)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> DeepLClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def _clip(value: str, limit: int = 60) -> str:
    value = value.replace("\n", " ")
    return value if len(value) <= limit else f"{value[:limit]}…"
