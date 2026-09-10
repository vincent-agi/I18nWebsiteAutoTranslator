# I18nWebsiteAutoTranslator

Generate **frontend i18n resource files** by translating a JSON file with the
[DeepL API](https://www.deepl.com/docs-api), keeping the key structure intact.

Maintaining translation JSON files by hand (Angular i18n, `react-i18next`,
Flutter ARB, …) is tedious: keeping the key tree consistent across languages,
chasing missing keys, pasting translations one by one. For content that changes
rarely, calling a translation API at runtime is overkill. This tool does the
translation **once, at build time**, and produces a static resource file your
app can ship as-is.

```
en.json  ──(DeepL)──▶  fr.json / es.json / de.json …
  keys preserved, only string values translated
```

## Features

- Translate one JSON file into another language.
- Every DeepL language is supported — pass the right code to `--source-lang` /
  `--target-lang` (see [DeepL docs](https://www.deepl.com/docs-api/translate-text)).
- Key structure is preserved; only string **values** are translated.
- Numbers, booleans and `null` pass through untouched.
- Free vs. Pro endpoint is auto-selected from the key (`:fx` suffix = Free).
- Transient errors (HTTP 429 / 5xx, network drops) are retried with back-off; on
  a hard failure the original string is kept, so the output file is never
  corrupted.
- Pure CLI — drops into any script, CI job or quality pipeline.

## Requirements

- Python **3.9+**
- A DeepL API key — a [free account](https://www.deepl.com/pro-api) gives you
  500 000 characters/month.

## Install

```bash
git clone https://github.com/vincent-agi/I18nWebsiteAutoTranslator.git
cd I18nWebsiteAutoTranslator

python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

pip install -e .                     # add "[dev]" to also get the test tools
```

## Configure the API key

Pick **one** of these (checked in this order):

| Method | How |
| --- | --- |
| CLI flag | `--api-key <key>` |
| Environment variable | `export DEEPL_API_KEY=<key>` |
| Key file | copy `deepl-key.json.example` to `deepl-key.json`, put your key in it |

`deepl-key.json` is git-ignored — **never commit your key**.

## Usage

```bash
# Translate the French sample menu into English
i18n-translate --source-lang FR --target-lang EN \
  --input-file examples/fr.json --output-file examples/fr.en.json

# Short flags
i18n-translate -s EN -t IT -i examples/en.json -o examples/en.it.json

# Help / version
i18n-translate --help
i18n-translate --version
```

Also runnable as `python -m i18n_translator …`. The legacy `python main.py …`
entry point still works (deprecated shim) and accepts the old `--origin-lang`
alias.

### Options

| Option | Description |
| --- | --- |
| `-s`, `--source-lang` | Source language code (e.g. `FR`). Alias: `--origin-lang`. |
| `-t`, `--target-lang` | Target language code (e.g. `EN`, `ES`, `DE`). |
| `-i`, `--input-file` | Path to the source JSON file. |
| `-o`, `--output-file` | Path to write the translated JSON file (parent dirs are created). |
| `--api-key` | DeepL API key; overrides the env var and key file. |
| `--key-file` | Key-file path (default `./deepl-key.json`). |
| `--indent` | Output JSON indentation (default `4`). |
| `-v`, `--verbose` | Debug logging. |

## Tests

```bash
pip install -e ".[dev]"
pytest -q            # unit tests, fully mocked — no network, no API key needed
ruff check .         # lint
```

## Documentation

- [`docs/utilisateur.md`](docs/utilisateur.md) — guide utilisateur (FR)
- [`docs/metier.md`](docs/metier.md) — documentation métier (FR)
- [`docs/technique.md`](docs/technique.md) — documentation technique (FR)

## Disclaimer

Machine translation is not perfect. **Review every generated file** before
shipping it. You are responsible for your use of this tool and of the DeepL API.

## License

GNU Affero General Public License v3.0 or later — see [`LICENSE`](LICENSE).
