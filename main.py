#!/usr/bin/env python3
"""Deprecated entry point — kept so existing ``python main.py ...`` calls keep working.

Prefer the installed command ``i18n-translate`` or ``python -m i18n_translator``.
See README.md and docs/ for the current usage.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from i18n_translator.cli import main  # noqa: E402

if __name__ == "__main__":
    print(
        "warning: main.py is deprecated; use `i18n-translate` or "
        "`python -m i18n_translator`.",
        file=sys.stderr,
    )
    raise SystemExit(main())
