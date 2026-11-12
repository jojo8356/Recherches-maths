# Compiler le dossier Lean sur votre machine

Deux projets indépendants, dans `dossiers/` :

| dossier | toolchain | dépendances | contenu |
|---|---|---|---|
| `dossiers/geom/` | `v4.36.0-rc2` | **Mathlib** | 51 théorèmes (géométrie, pont, queue, moteur du certificat) |
| `dossiers/lean/` | `v4.35.0` | **aucune** (noyau pur) | 15 théorèmes (plafond, T8, pont en arithmétique entière) |

---

## ATTENTION : la branche

Le travail récent (gestes 39 à 41, `verifier.sh`, `COMPILER.md`, lakefile corrigé) n'est **pas**
sur `main`, qui ne contient que le commit initial. Il est sur la branche
`arena/dfb03fac-recherches-maths`. Un `git clone` nu vous laisse sur `main` et **aucun des
fichiers récents n'existe** :

```
bash: dossiers/verifier.sh: Aucun fichier ou dossier de ce nom
```

Clonez la bonne branche, ou basculez dessus :

```bash
git clone -b arena/dfb03fac-recherches-maths https://github.com/jojo8356/Recherches-maths.git
# ou, dépôt déjà cloné :
git fetch origin && git checkout arena/dfb03fac-recherches-maths
```

Vérification en une ligne — doit afficher `verifier.sh` :

```bash
ls dossiers/verifier.sh
```

## Le plus court : un script fait tout

```bash
git clone -b arena/dfb03fac-recherches-maths \
    https://github.com/jojo8356/Recherches-maths.git
cd Recherches-maths
bash dossiers/verifier.sh
```

Il enchaîne les deux builds et les contrôles d'axiomes, et rend un bilan vert ou rouge.
Si vous préférez la main, lisez la suite.

---

## L'erreur la plus fréquente : être dans le mauvais dossier

```
~ ❯ cd dossiers/lean
cd: aucun fichier ou dossier de ce nom: dossiers/lean
```

`dossiers/` est **dans le dépôt cloné**, pas dans votre répertoire personnel. `lake` a ensuite
échoué en cherchant `lakefile.toml` dans `~` — il regarde le répertoire *courant*, et n'y trouvait
aucun projet. Il faut d'abord entrer dans le dépôt :

```bash
git clone https://github.com/jojo8356/Recherches-maths.git
cd Recherches-maths          # <-- l'étape oubliée
ls dossiers/                 # doit montrer : lean, geom, note, …
cd dossiers/lean
lake build
```

Si vous voyez déjà ces deux erreurs, **votre installation est correcte** : la toolchain
`v4.35.0` s'est bien installée (566 Mo téléchargés). Il ne manquait que le `cd`.

---

## 0. Prérequis

```bash
# Linux / macOS — installe elan, puis la toolchain épinglée par lean-toolchain
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
source "$HOME/.elan/env"        # ou : export PATH="$HOME/.elan/bin:$PATH"
```

Vérification : `elan --version` et `lake --version` doivent répondre.
Sur Windows, utilisez WSL2 (le chemin `curl | sh` n'existe pas).

---

## 1. Le projet sans dépendance (le plus rapide, ~30 s)

À faire en premier : il ne télécharge **rien** et dit tout de suite si votre installation marche.

```bash
cd dossiers/lean
lake build
```

Attendu : `Build completed successfully`, aucune erreur, aucun `sorry`.
Les 5 `#print axioms` du fichier `Pont.lean` doivent afficher exactement
`[propext, Classical.choice, Quot.sound]`.

---

## 2. Le projet Mathlib (le vrai contrôle, ~10 min la première fois)

```bash
cd dossiers/geom

lake update          # résout les dépendances selon lake-manifest.json (9 paquets épinglés)
lake exe cache get   # télécharge les .olean de Mathlib (~5 Go) — ÉVITE 40 min à 3 h de compilation
lake build
```

Attendu : `Build completed successfully`. Le journal de référence de l'audit annonce
`4 038 jobs` ; votre compte peut différer légèrement (versions de Lake).

### Puis les contrôles qui comptent vraiment

```bash
# Recompiler chaque fichier en affichant les #print axioms qu'il contient
lake env lean Geometrie.lean
lake env lean Queue.lean
lake env lean Pont.lean
lake env lean Boites.lean
lake env lean Boites_data.lean
```

**Ce qu'il faut regarder** — c'est le but de l'opération, pas le « build succeeded » :

- chaque `#print axioms` doit rendre **uniquement** `[propext, Classical.choice, Quot.sound]` ;
- aucune ligne `declaration uses 'sorry'` ne doit apparaître ;
- `'Boites.cell_of_fini' depends on axioms: [...]` doit être présent (c'est le théorème qui
  ramène la contrainte infinie à un calcul fini, celui dont dépend tout le certificat par boîte).

Pour un contrôle global d'un coup :

```bash
lake env lean Boites.lean 2>&1 | grep -E "sorry|depends on axioms"
```

Un `sorryAx` dans la sortie = échec, même si le build passe (Lean accepte `sorry` avec un
avertissement). C'est le piège classique : **`Build completed successfully` ne prouve pas
l'absence de `sorry`.**

---

## 3. Ce que ces commandes ne vérifient pas

Soyons précis sur le périmètre, pour éviter une fausse impression de « tout est certifié ».

- **Les 38 boîtes de données ne sont pas des preuves.** `Boites_data.lean` ne contient que des
  bornes, un seuil `T` et une clique par boîte. Aucune obligation de témoin n'y est écrite : le
  fichier compile, il ne prouve rien sur les boîtes.
- **Le certificat par boîte est prouvé en Python exact**, pas en Lean
  (`dossiers/note/obligations_boites.py`, boîtes 0 et 1, couverture 100 %). Le passage de ces
  calculs à des obligations Lean n'est pas fait.
- **`χ(ℝ²)` n'apparaît nulle part.** Aucun énoncé du dossier ne le concerne.

## 4. Si le build échoue

| symptôme | cause | remède |
|---|---|---|
| `error: unknown target 'Boites_data'` | `lakefile.toml` d'avant la correction | c'était le cas : `Boites_data` n'était pas déclaré. Corrigé. |
| `failed to create directory /var/tmp/geom-build` | `buildDir` pointait vers le bac à sable de l'audit | corrigé : chemins par défaut `.lake/` |
| `Invalid statement (at line 21)` sur `lakefile.toml` | j'y avais mis un commentaire `/- … -/`, qui est de la syntaxe **Lean**, pas **TOML** | corrigé : commentaires en `#` |
| `failed to download lean-4.36.0-rc2` | elan n'a pas la toolchain | `elan toolchain install leanprover/lean4:v4.36.0-rc2` |
| `cache` échoue / très long | pas d'accès au cache Mathlib | `lake build` compilera Mathlib depuis la source (long, ~10 Go de disque) |
| `push_neg` déprécié (avertissement) | Mathlib a renommé la tactique | **avertissement seulement**, sans effet sur les preuves |
| `cd: aucun fichier ou dossier de ce nom: dossiers/lean` | vous êtes dans `~`, pas dans le dépôt cloné | `cd Recherches-maths` d'abord (voir plus haut) |
| `dossiers/verifier.sh: Aucun fichier ou dossier de ce nom` | vous êtes sur `main`, où le fichier n'existe pas | `git checkout arena/dfb03fac-recherches-maths` |
| `bash: dossiers/[verifier.sh](http://verifier.sh): …` | un rendu markdown a transformé le nom en lien | taper la commande sans markdown : `bash dossiers/verifier.sh` |
| `no configuration file with a supported extension: ~/lakefile.toml` | même cause : `lake` cherche un projet dans le répertoire courant | se placer dans `dossiers/lean` ou `dossiers/geom` |
| `warning: could not canonicalize path: ~/.elan/toolchains` | bénin : dossier pas encore créé au premier lancement | ignorable, disparaît ensuite |

## 5. Un piège que j'ai créé en corrigeant (à savoir si vous voyez l'erreur)

En réparant `lakefile.toml`, j'y ai d'abord écrit des commentaires `/- … -/` — c'est la syntaxe
des commentaires **Lean**, pas **TOML**. Le fichier était donc invalide et `lake` aurait refusé de
le lire. Attrapé par une validation `tomllib` avant de vous livrer les commandes :

```bash
python3 -c "import tomllib;tomllib.load(open('lakefile.toml','rb'));print('ok')"
```

Les commentaires sont désormais en `#`. Si vous voyez `Invalid statement (at line 21)`, c'est
cette version-là du fichier : récupérez la version corrigée.

## 6. Renvoyer le résultat

Le plus utile est la sortie complète des cinq `lake env lean` du §2. Elle permet de confirmer
trois choses d'un coup : les 66 théorèmes compilent toujours, aucun `sorry` n'a été introduit,
et `Boites_data.lean` — réécrit au geste 40, **jamais compilé à ce jour** — est syntaxiquement
valide (`structure Boite`, rationnels `ℚ`, listes de décalages).

---

## Résultat du premier passage réel (12/11/2026, machine de l'utilisateur)

Toolchain `v4.35.0` puis `v4.36.0-rc2` installées, Mathlib décompressée (9 110 fichiers).
`Build completed successfully (4030 jobs)`.

### Ce qui est confirmé par un compilateur

| fichier | théorèmes | axiomes |
|---|---|---|
| `Geometrie.lean` | 17 (17 interrogés) | `[propext, Classical.choice, Quot.sound]` |
| `Pont.lean` | 6 (6 interrogés) | idem |
| `Queue.lean` | 28 déclarés, **5 interrogés** | les 5 : idem |
| `lean/Plafond.lean` | 6 déclarés, 4 interrogés | `[propext, Quot.sound]` |
| `lean/T8.lean` | 4 déclarés, 3 interrogés | `[propext, Quot.sound]` |
| `lean/Pont.lean` | 5 déclarés, 6 interrogés | idem |

Aucun `sorry`, aucun axiome supplémentaire. **`Boites.lean` n'est pas du lot** (voir plus bas).

### Deux défauts trouvés, et ils ne sont pas cosmétiques

**1. `lake build` ne compilait que `Geometrie`.** Le `lakefile.toml` porte
`defaultTargets = ["Geometrie"]` : `Queue`, `Pont` et `Boites` n'étaient **jamais** construits
par un `lake build` nu. Corrigé dans `verifier.sh`, qui nomme les cinq cibles.

**2. `Boites.lean` et `Boites_data.lean` ne compilent pas tels quels.**

```
Boites.lean:13:0: error: unknown module prefix 'Queue'
No directory 'Queue' or file 'Queue.olean' in the search path entries: …
```

`lake build` réussit pourtant : il s'arrête à `Geometrie` et ne visite jamais ces fichiers. Et
`lake env lean Boites.lean` échoue parce que `lake env` ne met **pas** le `lib/lean` de notre
propre paquet dans le `LEAN_PATH` — seulement ceux des dépendances. L'URL
`.lake/build/lib/lean` figure bien dans la liste des chemins cherchés, mais elle est **vide** au
moment de la recherche : viser `lake build <cible>` d'abord, puis relancer, devrait suffire.
À vérifier — je ne peux pas le faire sans accès Lean.

```
cd dossiers/geom
lake build Boites Boites_data     # construit les .olean de nos propres modules
lake env lean Boites.lean         # doit alors trouver Queue
```

**Conséquence à ne pas atténuer** : `Boites.clique_de_temoins`, `contrainte_auto`,
`cell_iff_translate` et `cell_of_fini` — les quatre théorèmes sur lesquels repose tout l'argument
par boîte — **ne sont pas vérifiés à ce jour**. Le `boites-check.log` du dossier date d'une
séance antérieure où l'environnement fonctionnait ; ce n'est pas une vérification.

### La leçon de méthode

Le premier `verifier.sh` a affiché « TOUT EST VERT » alors que `Boites.lean` était en erreur : il
comptait les axiomes dans les journaux et, ne trouvant rien dans un journal d'échec, concluait
« aucun axiome supplémentaire ». **Un fichier illisible passait pour un fichier vérifié.** Le
script détecte désormais les erreurs de compilation et les codes de sortie non nuls, et ne compte
que les théorèmes réellement interrogés.

---

## Second passage réel (12/11/2026) : `cell_of_fini` est vérifié

`lake build Boites Boites_data` a suffi (3 395 jobs). La cause identifiée était la bonne : le
`lib/lean` de notre propre paquet est vide tant qu'on ne l'a pas construit, donc `lake env lean`
ne trouvait pas `Queue.olean`.

**Les quatre théorèmes du moteur par boîte compilent, axiomes propres :**

```
'Boites.clique_de_temoins'    depends on axioms: [propext, Classical.choice, Quot.sound]
'Boites.contrainte_auto'      depends on axioms: [propext, Classical.choice, Quot.sound]
'Boites.cell_iff_translate'   depends on axioms: [propext, Classical.choice, Quot.sound]
'Boites.cell_of_fini'         depends on axioms: [propext, Classical.choice, Quot.sound]
```

`cell_of_fini` — la réduction de la contrainte infinie à un calcul fini, dont dépend tout
l'argument par boîte — est donc **vérifié par un compilateur**, ce qui n'était pas le cas au
geste 41. `Boites_data.lean` reste à confirmer (il doit passer par le même chemin).

Avertissements sans effet sur les preuves : `push_neg` déprécié (2 endroits), `Set.mem_setOf_eq`
déprécié, variable `hr` non référencée, argument `simp` inutilisé. Aucun ne touche un énoncé.

### Le compte n'est pas 66, mais 70 — et 19 n'étaient pas interrogés

Décompte réel par fichier :

| fichier | théorèmes | `#print axioms` présents |
|---|---|---|
| `geom/Geometrie.lean` | 17 | 17 |
| `geom/Queue.lean` | **28** | **5** |
| `geom/Pont.lean` | 6 | 6 |
| `geom/Boites.lean` | 4 | 4 |
| `lean/Plafond.lean` | 6 | 4 |
| `lean/T8.lean` | 4 | 3 |
| `lean/Pont.lean` | 5 | 5 (+1) |
| **total** | **70** | 51 |

Le dossier annonce « 66 théorèmes, 0 sorry » : le chiffre est faux, et surtout **19 théorèmes
n'étaient interrogés par aucun `#print axioms`**. Un théorème qui compile sans qu'on connaisse ses
axiomes n'est pas un résultat vérifié — c'est exactement le trou par lequel `sorryAx` passerait.

### `Axiomes.lean` : le trou bouché

`note/gen_axiomes.py` génère `dossiers/geom/Axiomes.lean` (55 théorèmes) et
`dossiers/lean/Axiomes.lean` (15 théorèmes), **70 au total, un `#print axioms` chacun**,
namespaces résolus automatiquement depuis les fichiers sources. Les deux fichiers sont déclarés
comme `lean_lib` et `verifier.sh` les contrôle.

```bash
lake env lean Axiomes.lean          # dans dossiers/geom puis dans dossiers/lean
```

Attendu : 55 puis 15 lignes `depends on axioms`, toutes dans
`[propext, Classical.choice, Quot.sound]` pour `geom`, dans `[propext, Quot.sound]` pour `lean`.
C'est le contrôle qui manquait, et il ne dépend plus de la répartition des `#print axioms` dans
les fichiers de preuve.

---

## « unknown module prefix 'Pont' / 'Queue' » : la règle à retenir

Rencontré deux fois, dans `Boites.lean` puis dans `Axiomes.lean` des deux projets. Une seule
cause, une seule règle.

**`lake env lean Fichier.lean` ne trouve pas nos propres modules si leurs `.olean` n'ont pas été
construits.** `lake env` met dans `LEAN_PATH` le `lib/lean` de nos paquets, mais ce dossier est
**vide** tant qu'on n'a pas construit. Les dépendances (Mathlib…) sont là, nos propres fichiers
non. D'où le message, qui liste les chemins cherchés — et où l'on voit `.lake/build/lib/lean`
présent mais inutilisable.

> **Règle : construire la cible avant de la lire.**
> ```bash
> lake build Axiomes          # construit les .olean ET les met dans le chemin
> lake env lean Axiomes.lean  # lit le fichier
> ```

`verifier.sh` applique désormais cette règle pour **chaque** fichier, sans exception.

### Deuxième défaut, trouvé en même temps

`dossiers/lean/Pont.lean` **n'était déclaré dans aucune `lean_lib`** — `lake build` ne le
construisait donc jamais, et `Axiomes.lean` échouait sur `unknown module prefix 'Pont'`. Il est
maintenant déclaré et ajouté aux `defaultTargets`. C'est cohérent avec ce que le dossier
affirmait déjà (5 théorèmes en noyau pur) : le fichier existait, il était juste invisible de Lake.

Bilan des cibles :

| projet | cibles |
|---|---|
| `dossiers/geom` | `Geometrie`, `Pont`, `Queue`, `Boites`, `Boites_data`, `Axiomes` |
| `dossiers/lean` | `Plafond`, `T8`, `Pont`, `Axiomes` |

### La séquence complète, corrigée

```bash
cd dossiers/geom
lake build                     # Geometrie (defaultTargets)
lake build Queue Pont Boites Boites_data Axiomes
lake env lean Axiomes.lean     # 55 théorèmes

cd ../lean
lake build                     # Plafond, T8, Pont
lake build Axiomes
lake env lean Axiomes.lean     # 15 théorèmes
```
