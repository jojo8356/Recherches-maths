# Compiler le dossier Lean sur votre machine

Deux projets indépendants, dans `dossiers/` :

| dossier | toolchain | dépendances | contenu |
|---|---|---|---|
| `dossiers/geom/` | `v4.36.0-rc2` | **Mathlib** | 51 théorèmes (géométrie, pont, queue, moteur du certificat) |
| `dossiers/lean/` | `v4.35.0` | **aucune** (noyau pur) | 15 théorèmes (plafond, T8, pont en arithmétique entière) |

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
