# Documentation métier

## Problème adressé

L'internationalisation d'un frontend repose sur des fichiers de ressources : un
fichier de traduction par langue, contenant les mêmes clés que la langue de
référence. Maintenir ces fichiers à la main pose trois difficultés récurrentes :

1. **Cohérence de structure** — chaque langue doit avoir le même arbre de clés ;
   une clé oubliée casse l'affichage.
2. **Coût de production** — copier-coller les traductions une par une est long
   et sans valeur ajoutée.
3. **Dérive dans le temps** — à chaque évolution du texte source, il faut
   répercuter la modification dans toutes les langues.

## Proposition de valeur

L'outil génère les fichiers de ressources **au moment du build**, à partir du
fichier de la langue pivot, en appelant l'API DeepL. Le frontend charge ensuite
un fichier statique.

```
Langue pivot (fr.json)  ──►  i18n-translate  ──►  en.json, es.json, de.json …
                                   │
                                   └─ API DeepL, une fois, hors ligne de production
```

### Pourquoi pas d'appel d'API à l'exécution

Pour du contenu **peu changeant** (menus, pages vitrines, libellés d'interface,
mentions légales), traduire à chaque affichage serait :

- **coûteux** — chaque vue consomme du quota API ;
- **lent** — latence réseau ajoutée au rendu ;
- **fragile** — l'app dépend de la disponibilité d'un service tiers ;
- **non déterministe** — le même texte peut varier d'un appel à l'autre.

Un fichier de ressources statique élimine ces quatre points : coût unique au
build, aucune latence, fonctionnement hors ligne, résultat figé et versionné.

## Cas d'usage typiques

| Contexte | Adapté ? | Remarque |
| --- | --- | --- |
| Site vitrine multilingue | Oui | Contenu stable, volume faible. |
| Menu de restaurant, catalogue court | Oui | Regénéré à chaque changement de carte. |
| Libellés d'interface d'une application web / mobile | Oui | Le cœur de la cible. |
| Application à contenu généré par les utilisateurs | Non | Contenu dynamique : traduction à la volée requise. |
| Volumes très importants, mises à jour continues | Partiellement | Le coût DeepL et le temps de build deviennent significatifs. |

## Bénéfices

- **Maîtrise des coûts** — la consommation DeepL est bornée et connue (voir
  ci-dessous), déclenchée uniquement lors d'une régénération.
- **Performance** — zéro appel réseau côté utilisateur final.
- **Robustesse** — aucune dépendance d'exécution à un service tiers.
- **Cohérence des clés** — l'arbre de clés de la source est reproduit à
  l'identique dans chaque langue, par construction.
- **Traçabilité** — les fichiers générés sont versionnés dans le dépôt et
  relisibles en revue de code.
- **Intégration** — CLI à code de sortie standard, insérable dans n'importe
  quel pipeline qualité.

## Limites et points de vigilance

- **Qualité de la traduction automatique** — correcte mais imparfaite : noms
  propres, unités, termes métier, tournures idiomatiques doivent être relus.
  Une étape de relecture humaine reste nécessaire avant publication.
- **Pas de glossaire** dans cette version — la terminologie propre au produit
  n'est pas garantie constante.
- **Traduction intégrale à chaque exécution** — l'outil retraduit tout le
  fichier, même si une seule chaîne a changé (voir *Évolutions envisagées* dans
  la documentation technique).
- **Formats sensibles** — les chaînes contenant des variables d'interpolation
  (`{{name}}`, `%s`, `:count`) sont envoyées telles quelles à DeepL ; vérifier
  que les marqueurs sont préservés dans la sortie.

## Coûts DeepL

| Offre | Volume inclus | Clé |
| --- | --- | --- |
| API Free | 500 000 caractères / mois | se termine par `:fx` |
| API Pro | facturation à l'usage au-delà d'un forfait | sans suffixe `:fx` |

Le décompte se fait sur le **nombre de caractères des valeurs traduites**,
multiplié par le nombre de langues cibles et par le nombre de régénérations.
Exemple : un fichier de 20 000 caractères × 5 langues × 4 régénérations par mois
= 400 000 caractères, soit sous le plafond gratuit.

## Workflow recommandé

1. **Langue pivot unique** — une seule langue fait foi (souvent le français ou
   l'anglais). Tous les textes sont d'abord écrits dans cette langue.
2. **Régénération à chaque changement** — dès que la source évolue, relancer
   `i18n-translate` pour toutes les langues cibles.
3. **Relecture** — faire valider les fichiers générés par un locuteur de chaque
   langue, au moins sur les écrans visibles.
4. **Versionnement** — committer les fichiers générés ; les diffs permettent de
   voir précisément ce qui a changé.
5. **Automatisation** — brancher l'étape sur la CI, avec la clé DeepL en secret.

## Indicateurs de suivi

- Nombre de caractères traduits par mois (à rapprocher du quota DeepL).
- Nombre de clés par langue (doit être identique à la langue pivot).
- Délai entre un changement de texte source et sa régénération dans les autres
  langues.
- Taux de chaînes corrigées en relecture (qualité perçue de la traduction
  automatique).
