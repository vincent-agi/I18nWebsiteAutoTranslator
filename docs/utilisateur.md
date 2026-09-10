# Documentation utilisateur

Guide pas à pas pour produire un fichier de ressources de traduction avec
`i18n-translate`.

## À qui s'adresse cet outil

Développeur ou intégrateur qui maintient des fichiers d'internationalisation
(i18n) au format JSON pour un frontend : Angular i18n, `react-i18next`,
`vue-i18n`, Flutter (ARB converti en JSON), etc. L'outil traduit **une fois**
les valeurs d'un fichier JSON vers une autre langue, en conservant l'arbre de
clés. Le frontend charge ensuite un fichier statique, sans appel d'API à
l'exécution.

## Prérequis

- Python **3.9 ou supérieur** (`python --version`).
- Une clé d'API DeepL. Un [compte gratuit](https://www.deepl.com/pro-api) offre
  500 000 caractères par mois.

## Installation

```bash
git clone https://github.com/vincent-agi/I18nWebsiteAutoTranslator.git
cd I18nWebsiteAutoTranslator

python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate

pip install -e .
```

La commande `i18n-translate` est alors disponible dans l'environnement virtuel.

## Obtenir une clé DeepL

1. Créer un compte sur <https://www.deepl.com/pro-api>.
2. Dans l'espace compte, section **API keys**, copier la clé.
3. Une clé gratuite se termine par `:fx`. L'outil détecte automatiquement le bon
   point d'accès (gratuit ou payant).

## Renseigner la clé

Trois méthodes, évaluées dans cet ordre (la première trouvée gagne) :

| Priorité | Méthode | Mise en place |
| --- | --- | --- |
| 1 | Option CLI | `--api-key VOTRE_CLE` |
| 2 | Variable d'environnement | `export DEEPL_API_KEY=VOTRE_CLE` |
| 3 | Fichier de clé | copier `deepl-key.json.example` en `deepl-key.json`, y coller la clé |

> Le fichier `deepl-key.json` est ignoré par git. **Ne jamais committer la
> clé** dans le dépôt.

## Traduire un fichier

Exemple : traduire le menu de restaurant fourni (`examples/fr.json`, en
français) vers l'anglais.

```bash
i18n-translate \
  --source-lang FR \
  --target-lang EN \
  --input-file  examples/fr.json \
  --output-file examples/fr.en.json
```

Version courte :

```bash
i18n-translate -s FR -t EN -i examples/fr.json -o examples/fr.en.json
```

Sortie console attendue :

```
INFO Translating 128 string(s) from FR to EN
INFO Done. Wrote examples/fr.en.json
```

Le fichier produit a **exactement les mêmes clés** que la source ; seules les
chaînes de caractères sont traduites. Les nombres, booléens et `null` sont
recopiés tels quels.

## Options de la ligne de commande

| Option | Rôle | Défaut |
| --- | --- | --- |
| `-s`, `--source-lang` | Code langue source (ex. `FR`). Alias hérité : `--origin-lang`. | obligatoire |
| `-t`, `--target-lang` | Code langue cible (ex. `EN`, `ES`, `DE`). | obligatoire |
| `-i`, `--input-file` | Chemin du JSON source. | obligatoire |
| `-o`, `--output-file` | Chemin du JSON traduit (les dossiers parents sont créés). | obligatoire |
| `--api-key` | Clé DeepL ; prioritaire sur la variable d'environnement et le fichier. | — |
| `--key-file` | Chemin du fichier de clé. | `./deepl-key.json` |
| `--indent` | Indentation du JSON de sortie. | `4` |
| `-v`, `--verbose` | Journalisation détaillée (debug). | désactivé |
| `--version` | Affiche la version puis quitte. | — |
| `--help` | Affiche l'aide puis quitte. | — |

## Codes de langue

La liste complète est dans la documentation DeepL :
<https://www.deepl.com/docs-api/translate-text>. Utiliser le code tel quel
(`EN`, `EN-GB`, `PT-BR`, …) ; la casse n'a pas d'importance.

## Générer plusieurs langues

Un fichier cible par appel. En script shell :

```bash
for lang in EN ES DE IT; do
  i18n-translate -s FR -t "$lang" \
    -i src/i18n/fr.json \
    -o "src/i18n/$(echo "$lang" | tr '[:upper:]' '[:lower:]').json"
done
```

## Intégration dans un pipeline

`i18n-translate` renvoie un **code de sortie** :

- `0` : succès.
- `1` : erreur (clé absente, fichier source introuvable, JSON invalide).
- `130` : interruption clavier.

Il s'intègre donc directement dans un `Makefile`, un job CI ou un hook de
build. La clé est fournie via `DEEPL_API_KEY` (secret CI).

## Erreurs fréquentes

| Message | Cause | Solution |
| --- | --- | --- |
| `No DeepL API key found...` | Aucune des trois méthodes n'a fourni de clé. | Définir `DEEPL_API_KEY` ou créer `deepl-key.json`. |
| `Input file not found: ...` | Chemin `--input-file` incorrect. | Vérifier le chemin (relatif au dossier courant). |
| `... is not valid JSON: ...` | Le fichier source est mal formé. | Valider le JSON (`python -m json.tool fichier`). |
| `DeepL error 403 ...` dans les logs | Clé invalide ou révoquée. | Régénérer une clé sur DeepL. Le fichier est quand même écrit, avec le texte d'origine à la place des traductions échouées. |
| `DeepL transient error 429` | Quota de requêtes momentané atteint. | L'outil réessaie automatiquement ; relancer si l'erreur persiste. |

## Relecture

La traduction automatique n'est pas parfaite (noms propres, unités, formats de
prix, termes métier). **Relire chaque fichier généré** avant mise en
production.
