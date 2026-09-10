# Documentation technique

## Vue d'ensemble

Paquet Python `i18n_translator` exposant une commande `i18n-translate`. Il lit
un fichier JSON, traduit récursivement ses valeurs `str` via l'API DeepL, puis
écrit un JSON de même structure.

```
┌──────────┐   argparse    ┌──────────┐   resolve_api_key   ┌──────────┐
│   cli    │──────────────▶│  config  │────────────────────▶│  clé API │
└────┬─────┘               └──────────┘                     └──────────┘
     │ json.loads(input)
     ▼
┌──────────────┐  translate_tree (récursif)   ┌──────────────┐  HTTP POST  ┌────────┐
│  translator  │────────────────────────────▶ │    deepl     │───────────▶ │ DeepL  │
└──────┬───────┘   pour chaque str leaf       └──────────────┘  + retry    └────────┘
       │ json.dumps(result)
       ▼
   output-file
```

## Structure du dépôt

```
src/i18n_translator/
  __init__.py      version du paquet (importlib.metadata)
  __main__.py      support de `python -m i18n_translator`
  cli.py           parsing des arguments, orchestration, codes de sortie
  config.py        résolution de la clé API (CLI > env > fichier)
  deepl.py         client HTTP DeepL : endpoints, auth, retry/back-off
  translator.py    parcours récursif de la structure JSON
  errors.py        hiérarchie d'exceptions
main.py            shim de compatibilité (déprécié) pour `python main.py`
tests/             suite pytest, 100 % mockée
examples/          fichiers JSON d'exemple (fr / en / es)
docs/              cette documentation
pyproject.toml     métadonnées, dépendances, config pytest/ruff
.github/workflows/ci.yml   intégration continue
```

## Modules

### `config.py`

`resolve_api_key(cli_value, key_file)` renvoie la clé selon l'ordre :

1. valeur passée à `--api-key` ;
2. variable d'environnement `DEEPL_API_KEY` ;
3. champ `deepl-key` du fichier `key_file` (défaut `./deepl-key.json`).

Lève `ConfigError` si aucune source ne fournit de clé, ou si le fichier existe
mais est mal formé.

### `deepl.py`

- `endpoint_for(api_key)` — renvoie `FREE_ENDPOINT` si la clé se termine par
  `:fx`, sinon `PRO_ENDPOINT`.
- `DeepLClient` — encapsule une `requests.Session` réutilisée pour tout le
  fichier (connexion HTTP maintenue). Authentification par en-tête
  `Authorization: DeepL-Auth-Key <clé>` (méthode recommandée par DeepL, en
  remplacement du paramètre `auth_key` historique).
  - `translate(text, *, source_lang, target_lang) -> str`
  - Chaîne vide ou uniquement blanche : renvoyée sans appel réseau.
  - HTTP 200 : renvoie `translations[0]["text"]`. Corps inattendu : renvoie le
    texte d'origine.
  - HTTP 429 ou 5xx, ou erreur réseau : nouvelle tentative, back-off linéaire
    (`backoff * numéro_de_tentative`), jusqu'à `max_retries`.
  - Autre code (4xx) : erreur définitive, renvoie le texte d'origine.
  - Épuisement des tentatives : renvoie le texte d'origine.
  - Gestionnaire de contexte (`with DeepLClient(...) as client:`) qui ferme la
    session en sortie.

Paramètres par défaut : `timeout=15.0`, `max_retries=3`, `backoff=1.0`.

**Principe de résilience** : un échec partiel ne doit jamais corrompre le
fichier de sortie. À défaut de traduction, la valeur source est conservée.

### `translator.py`

- `translate_tree(value, client, *, source_lang, target_lang)` — parcours
  récursif :
  - `str` → `client.translate(...)` ;
  - `dict` → nouveau dict, clés inchangées, valeurs traduites récursivement ;
  - `list` → nouvelle liste, éléments traduits récursivement ;
  - tout le reste (`int`, `float`, `bool`, `None`) → recopié tel quel.
  - L'objet d'entrée n'est jamais muté (copie profonde implicite).
- `count_strings(value)` — compte les feuilles `str`, pour le log de
  progression.
- `SupportsTranslate` — `Protocol` décrivant le contrat attendu du client, ce
  qui permet d'injecter un faux client dans les tests sans dépendre de
  `DeepLClient`.

### `cli.py`

- `build_parser()` — définit les options (voir README / doc utilisateur).
  `--source-lang` accepte l'alias historique `--origin-lang`.
- `--credits` est intercepté avant `argparse` pour rester utilisable seul.
- `main(argv=None) -> int` — codes de sortie :
  - `0` succès ;
  - `1` toute `I18nTranslatorError` (clé absente, source introuvable, JSON
    invalide) ;
  - `130` `KeyboardInterrupt`.
- Sortie JSON : `json.dumps(..., ensure_ascii=False, indent=args.indent)` suivi
  d'un saut de ligne final ; les dossiers parents de `--output-file` sont créés.

### `errors.py`

```
I18nTranslatorError
├── ConfigError   (clé API non résolue)
└── DeepLError    (erreur client irrécupérable, ex. clé vide)
```

## Contrat DeepL

| Élément | Valeur |
| --- | --- |
| Endpoint Free | `https://api-free.deepl.com/v2/translate` |
| Endpoint Pro | `https://api.deepl.com/v2/translate` |
| Auth | en-tête `Authorization: DeepL-Auth-Key <clé>` |
| Corps | `text`, `source_lang` (majuscules), `target_lang` (majuscules) |
| Réponse OK | `{"translations": [{"text": "..."}]}` |
| Réessayés | `429`, `5xx`, erreurs réseau |
| Non réessayés | autres `4xx` |

Référence des codes de langue :
<https://www.deepl.com/docs-api/translate-text>.

## Installation développeur

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Dépendances :

- exécution : `requests>=2.31,<3` ;
- développement : `pytest`, `pytest-cov`, `responses`, `ruff`.

## Tests

```bash
pytest -q
```

- Aucun accès réseau, aucune clé requise : les appels HTTP sont simulés avec
  [`responses`](https://github.com/getsentry/responses), le parcours récursif
  est testé avec un faux client (`FakeClient`).
- `tests/conftest.py` fournit la fixture `api_key` (`"test-key:fx"`).
- Couverture : `config` (ordre de résolution, erreurs), `deepl` (succès,
  4xx/429/5xx, corps malformé, header d'auth, sélection d'endpoint), `translator`
  (feuilles str uniquement, non-mutation, clés préservées), `cli` (bout en
  bout, codes de sortie).
- `pyproject.toml` fixe `pythonpath = ["src"]` : `pytest` fonctionne sans
  installation préalable.

## Lint

```bash
ruff check .
```

Règles activées : `E`, `F`, `I` (imports), `UP` (modernisation syntaxe), `B`
(bugbear), `SIM` (simplifications). `line-length = 110`, cible `py39`.

## Intégration continue

`.github/workflows/ci.yml` : matrice Python 3.9 → 3.13, sur `push` et
`pull_request` vers `main`.

```
checkout@v4 → setup-python@v5 (cache pip) → pip install -e ".[dev]" → ruff check . → pytest -q
```

> Le fichier de workflow précédent s'appelait `.github/workflows/ci` (sans
> extension) et n'était donc pas exécuté par GitHub Actions. Il est renommé en
> `ci.yml`.

## Packaging

- Backend de build : `hatchling`.
- `[project.scripts]` : `i18n-translate = "i18n_translator.cli:main"`.
- `src`-layout ; le wheel n'embarque que `src/i18n_translator`.
- Version unique dans `pyproject.toml`, relue à l'exécution via
  `importlib.metadata.version("i18n-translator")`.

## Décisions de conception

- **Structure JSON immuable** — `translate_tree` ne modifie jamais l'entrée ;
  facilite les tests et évite les effets de bord.
- **Repli sur le texte d'origine** — préféré à une exception : un fichier
  partiellement traduit reste exploitable et diffable.
- **Auth par en-tête** — méthode recommandée par DeepL ; le paramètre
  `auth_key` dans le corps est considéré comme legacy.
- **Session partagée** — une seule connexion HTTP par exécution, plutôt qu'une
  par chaîne.
- **Pas d'asynchrone** — le goulot est le quota DeepL, pas le parallélisme
  local ; la simplicité prime pour un outil de build.
- **Shim `main.py`** — conservé pour ne pas casser les scripts existants
  (`python main.py --origin-lang ...`).

## Changements par rapport à la version précédente

| Avant | Après |
| --- | --- |
| Script unique `main.py` | Paquet `src/i18n_translator/` + entry point `i18n-translate` |
| Clé lue uniquement dans `deepl-key.json` (chemin codé en dur) | `--api-key` > `DEEPL_API_KEY` > `--key-file` |
| `deepl-key.json` (avec clé réelle) suivi par git | Retiré du suivi ; `deepl-key.json.example` fourni ; `.gitignore` déjà en place |
| Auth via paramètre `auth_key` dans le corps | En-tête `Authorization: DeepL-Auth-Key` |
| `print()` pour les diagnostics | Module `logging` |
| Aucune reprise sur erreur | Retry + back-off sur 429 / 5xx / erreurs réseau |
| `tests.py` cassé (`from requests import patch`, `translate_dict` inexistant) | Suite `pytest` mockée, verte sur 3.9 → 3.13 |
| `.github/workflows/ci` (sans extension, jamais exécuté) | `.github/workflows/ci.yml`, matrice de versions, lint + tests |
| `--origin-lang` | `--source-lang` (`--origin-lang` conservé en alias) |
| Pas de packaging | `pyproject.toml` (hatchling), `ruff`, dépendances épinglées |

## Évolutions envisagées

- **Traduction incrémentale** — comparer avec le fichier cible existant et ne
  retraduire que les clés nouvelles ou modifiées (économie de quota).
- **Multi-cibles en une passe** — `--target-lang EN,ES,DE`.
- **Glossaire DeepL** — pour figer la terminologie produit.
- **Cache local** — mémoriser `(texte, langue) → traduction` entre exécutions.
- **Préservation des marqueurs d'interpolation** — protéger `{{var}}`, `%s`,
  `:count` via les balises `<x>` ignorées de DeepL.
