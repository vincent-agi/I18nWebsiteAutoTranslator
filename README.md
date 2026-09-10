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

## Docker

The tool ships as a small multi-stage image (Python slim + an isolated venv,
non-root, no build tools in the final layer). Published on every push:

- **GHCR:** `ghcr.io/vincent-agi/i18nwebsiteautotranslator`
- **Docker Hub:** `vincentagi/i18n-translator` *(when the `DOCKERHUB_USERNAME`
  repo variable and `DOCKERHUB_TOKEN` secret are set)*

Tags: `latest` (default branch), plus `X`, `X.Y`, `X.Y.Z` on `vX.Y.Z` git tags.

### One-shot run (throwaway container)

`--rm` removes the container the moment it exits; nothing is left running. Mount
the directory that holds your JSON files at `/work` and run paths relative to it:

```bash
docker run --rm \
  -e DEEPL_API_KEY \
  -v "$PWD":/work \
  ghcr.io/vincent-agi/i18nwebsiteautotranslator:latest \
  -s FR -t EN -i examples/fr.json -o examples/fr.en.json
```

The key can also come from a `deepl-key.json` in the mounted directory instead of
`-e DEEPL_API_KEY`. Add `--user "$(id -u):$(id -g)"` so the output file is owned
by you and not by root.

### Helper script (run + cleanup)

`scripts/i18n-translate-docker.sh` wraps the above: it runs as your host
uid/gid by default, and `--cleanup` removes the image and prunes dangling
layers afterwards (Docker fills disk fast when images pile up).

```bash
DEEPL_API_KEY=xxx scripts/i18n-translate-docker.sh -- \
  -s FR -t EN -i examples/fr.json -o examples/fr.en.json

# translate, then drop the image + dangling layers
DEEPL_API_KEY=xxx scripts/i18n-translate-docker.sh --cleanup -- \
  -s EN -t DE -i en.json -o de.json
```

Override the image with `I18N_TRANSLATE_IMAGE`, the mounted dir with
`I18N_TRANSLATE_WORKDIR`. `scripts/i18n-translate-docker.sh --help` lists it all.

### Build locally

```bash
docker build -t i18n-translator .
```

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
