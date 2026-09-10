"""Command-line entry point for ``i18n-translate``."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from . import __version__
from .config import resolve_api_key
from .deepl import DeepLClient
from .errors import I18nTranslatorError
from .translator import count_strings, translate_tree

_LOG = logging.getLogger("i18n_translator")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="i18n-translate",
        description=(
            "Translate the string values of a JSON i18n file with DeepL, "
            "keeping the key structure intact."
        ),
    )
    parser.add_argument(
        "-s", "--source-lang", "--origin-lang", dest="source_lang", required=True,
        metavar="LANG", help="Source language code (e.g. FR, EN).",
    )
    parser.add_argument(
        "-t", "--target-lang", dest="target_lang", required=True,
        metavar="LANG", help="Target language code (e.g. EN, ES, DE).",
    )
    parser.add_argument(
        "-i", "--input-file", dest="input_file", required=True, type=Path,
        metavar="PATH", help="Path to the source JSON file.",
    )
    parser.add_argument(
        "-o", "--output-file", dest="output_file", required=True, type=Path,
        metavar="PATH", help="Path to write the translated JSON file.",
    )
    parser.add_argument(
        "--api-key", metavar="KEY",
        help="DeepL API key (overrides DEEPL_API_KEY and the key file).",
    )
    parser.add_argument(
        "--key-file", type=Path, default=Path("deepl-key.json"), metavar="PATH",
        help="JSON file holding a 'deepl-key' field (default: ./deepl-key.json).",
    )
    parser.add_argument(
        "--indent", type=int, default=4, metavar="N",
        help="Indentation of the output JSON (default: 4).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


_CREDITS = "i18n-translator — JSON translation with DeepL. Developed by Vincent AGI."


def _translate_file(args: argparse.Namespace) -> None:
    api_key = resolve_api_key(args.api_key, args.key_file)

    try:
        source_data = json.loads(args.input_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise I18nTranslatorError(f"Input file not found: {args.input_file}") from exc
    except json.JSONDecodeError as exc:
        raise I18nTranslatorError(f"{args.input_file} is not valid JSON: {exc}") from exc

    total = count_strings(source_data)
    _LOG.info(
        "Translating %d string(s) from %s to %s",
        total, args.source_lang.upper(), args.target_lang.upper(),
    )

    with DeepLClient(api_key) as client:
        translated = translate_tree(
            source_data, client,
            source_lang=args.source_lang, target_lang=args.target_lang,
        )

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(translated, ensure_ascii=False, indent=args.indent) + "\n",
        encoding="utf-8",
    )
    _LOG.info("Done. Wrote %s", args.output_file)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--credits" in argv:
        print(_CREDITS)
        return 0

    args = build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    try:
        _translate_file(args)
    except I18nTranslatorError as exc:
        _LOG.error("%s", exc)
        return 1
    except KeyboardInterrupt:  # pragma: no cover
        _LOG.error("Interrupted")
        return 130
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
