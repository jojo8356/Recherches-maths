# Accès au toolchain Lean : diagnostic et demande d'ouverture

**Date** : 2026-11-12 · **Geste** 41 · **Script** `diag_lean_acces.py` (exit 1) · **Journal**
`diag_lean_acces.log`

## En une ligne

La compilation n'est pas bloquée par `elan` ni par une erreur de commande : elle est bloquée par
**six hôtes sur les dix nécessaires**, et aucun de ceux qui répondent ne sert d'artefact Lean. Le
geste précédent annonçait « trois hôtes » : c'est faux, et le compte exact est ci-dessous.

## Ce qui a été essayé, dans l'ordre, et ce que chaque essai a donné

| piste | résultat |
|---|---|
| `elan` via `raw.githubusercontent.com/elan-init.sh` | **bloqué** (TLS coupé) |
| `elan` via `github.com/…/releases/download/…` | 302 vers `objects.githubusercontent.com` → **bloqué** |
| toolchain `lean4` via `releases.lean-lang.org` (voie d'`elan`, cf. `setup.log`) | **bloqué** |
| toolchain `lean4` via les artefacts de release GitHub | **bloqué** (`release-assets.githubusercontent.com`) |
| PyPI : `lean4`, `lean`, `pyelan` | **aucun binaire** — 0,01 à 0,37 Mo, wrappers et homonymes |
| PyPI : `lean-dojo` (67 Mo, seul paquet volumineux) | **aucun binaire** — 67 Mo de jeu de données de benchmark, inspecté fichier par fichier |
| npm : `@leanprover/*`, `lean4-wasm`, `elan` | **aucun binaire** — interfaces, coloration syntaxique ; sept requêtes de recherche |
| reliquats de la séance précédente (`~/.elan`, `/var/tmp/geom-*`) | **absents** — le bac à sable est neuf |
| cache Mathlib (`lake exe cache get`) | **bloqué** (`leanprover-community.github.io`, `mathlib.cache.azureedge.net`) |
| compiler Lean 4 depuis la source via `codeload` | possible en principe (accès 200) mais **exclu en pratique** : 2 cœurs, 3,8 Go de RAM ; Mathlib demande ~10 Go et plusieurs heures |

## Les hôtes à ouvrir, avec les volumes

| hôte | rôle | volume |
|---|---|---|
| `objects.githubusercontent.com` | cible du 302 des releases (elan) | 5 Mo |
| `release-assets.githubusercontent.com` | autre nom des artefacts de release | — |
| `raw.githubusercontent.com` | `elan-init.sh` | 20 Ko |
| `releases.lean-lang.org` | toolchain `lean4` (voie normale d'`elan`) | 608 Mo |
| `leanprover-community.github.io` | cache Mathlib | ~5 Go |
| `mathlib.cache.azureedge.net` | repli du cache | — |

Les trois premiers ne servent qu'à amorcer `elan` ; `releases.lean-lang.org` porte la toolchain.
**Le quatrième est le seul non négociable pour Mathlib** : sans le cache, il faut construire
Mathlib, ce qui n'est pas faisable dans ce bac à sable. Les dépendances (`batteries`, `aesop`,
`Qq`, `proofwidgets`…) viennent de `codeload.github.com`, qui répond — mais elles ne suffisent
pas : `Geometrie.lean` et `Queue.lean` importent `Mathlib.Analysis.Convex.Topology` et
`Mathlib.Topology.Order.IntermediateValue`, donc **le toolchain seul ne compilerait rien**.

## Une erreur de méthode, corrigée

La première version du diagnostic testait `socket.create_connection((hote, 443))`. Elle
concluait « un seul hôte bloqué » — **faux pour six d'entre eux**. La raison est un proxy de
sortie transparent : il accepte la connexion TCP, puis coupe au `ClientHello` TLS. Un test de
connexion est donc un faux positif systématique ; il faut aller jusqu'à la requête HTTP. Le
symptôme côté client est `SSL_ERROR_SYSCALL`, jamais un refus de connexion — ce qui explique
pourquoi le diagnostic précédent attribuait l'échec à « releases GitHub » sans voir que
`releases.lean-lang.org` et le cache Mathlib étaient tombés pour la même raison.
`diag_lean_acces.py` teste maintenant une requête HTTPS réelle et accepte toute réponse HTTP
(même 4xx) comme preuve que le TLS passe.

## Ce que je ne peux pas faire depuis ici

Ce n'est pas une lacune de méthode : c'est une liste d'accès qui ne m'appartient pas. Je ne peux
pas ouvrir ces hôtes moi-même, et il n'existe aucun chemin de substitution depuis les dépôts
autorisés (`pypi`, `npm`) — vérifié, pas supposé.

**Deux issues possibles :**

1. **Ouvrir les quatre hôtes nécessaires** (`objects.githubusercontent.com`,
   `releases.lean-lang.org`, `raw.githubusercontent.com`,
   `leanprover-community.github.io`) dans la configuration réseau du bac à sable, puis relancer
   `diag_lean_acces.py` (il doit rendre 0) avant `lake update && lake exe cache get &&
   lake build Queue Pont Boites`.
2. **Compiler ailleurs** : n'importe quelle machine avec Lean et Mathlib. `dossiers/geom/` est
   autonome (`lakefile.toml`, `lake-manifest.json` épinglé, `lean-toolchain`
   `v4.36.0-rc2`) ; il suffit d'y lancer les quatre commandes. C'est aussi la seule voie qui
   vérifie `Boites_data.lean` en forme corrigée, écrit au geste 40 mais jamais compilé.

## Conséquence sur l'état du dossier, dite sans détour

Les **66 théorèmes** du dossier sont ceux des journaux du 03/11. Rien n'a été recompilé depuis.
En particulier :

- `Boites.clique_de_temoins`, `contrainte_auto`, `cell_iff_translate`, `cell_of_fini` : cités
  partout dans l'audit, **non revérifiés aujourd'hui** ;
- `Boites_data.lean`, réécrit au geste 40 en forme corrigée (`structure Boite`, seuil par
  boîte), **n'a jamais vu `lake build`** — la structure et la syntaxe `ℚ` ne sont pas vérifiées ;
- le certificat par boîte est prouvé **en Python exact**, pas en Lean. Le passage « données
  Python → obligations Lean » est écrit mais non validé par un compilateur.
