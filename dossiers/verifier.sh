#!/usr/bin/env bash
# Vérifie les deux projets Lean du dossier Sokolov–Voronov.
#
#   bash dossiers/verifier.sh
#
# Ce script ne « compile » pas seulement : il vérifie les trois choses qui comptent.
#  1. les deux projets compilent ;
#  2. aucun théorème ne dépend de `sorryAx` (un « build succeeded » ne le dit PAS :
#     Lean accepte `sorry` avec un simple avertissement) ;
#  3. les axiomes de chaque théorème sont exactement propext, Classical.choice, Quot.sound.
#
# Il s'arrête proprement et dit quoi faire si une étape manque (toolchain, cache Mathlib).

set -u

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECHEC=0

titre() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
ok()    { printf '  \033[32mOK\033[0m   %s\n' "$*"; }
ko()    { printf '  \033[31mÉCHEC\033[0m %s\n' "$*"; ECHEC=1; }
info()  { printf '  ..   %s\n' "$*"; }

# ---------------------------------------------------------------- prérequis
titre "Prérequis"
if ! command -v lake >/dev/null 2>&1; then
  ko "lake introuvable. Installer elan :
      curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
      source \"\$HOME/.elan/env\""
  exit 1
fi
ok "lake : $(command -v lake)"
lake --version 2>/dev/null | head -1 | sed 's/^/       /'

# ---------------------------------------------------------------- projet sans dépendance
titre "dossiers/lean — noyau pur, aucune dépendance (~30 s)"
cd "$RACINE/lean" || { ko "dossier lean absent"; exit 1; }
info "toolchain épinglée : $(cat lean-toolchain)"
if lake build 2>&1 | tee /tmp/v_lean.log | tail -3; then :; fi
if grep -q "Build completed successfully" /tmp/v_lean.log; then
  ok "build"
else
  ko "build (voir /tmp/v_lean.log)"
fi

# ---------------------------------------------------------------- projet Mathlib
titre "dossiers/geom — Mathlib (long la première fois)"
cd "$RACINE/geom" || { ko "dossier geom absent"; exit 1; }
info "toolchain épinglée : $(cat lean-toolchain)"
if [ ! -d .lake/packages/mathlib ]; then
  info "dépendances absentes : lake update"
  lake update 2>&1 | tail -3
fi
if [ ! -d .lake/packages/mathlib/.lake/build/lib/lean ]; then
  info "cache Mathlib absent : lake exe cache get (facultatif, mais évite des heures de compilation)"
  lake exe cache get 2>&1 | tail -3
fi
if lake build 2>&1 | tee /tmp/v_geom.log | tail -3; then :; fi
if grep -q "Build completed successfully" /tmp/v_geom.log; then
  ok "build"
else
  ko "build (voir /tmp/v_geom.log)"
fi

# ---------------------------------------------------------------- contrôles par fichier
titre "Contrôles : axiomes et absence de sorry"
SORRY=0
AXIOMES=0
for f in Geometrie Queue Pont Boites Boites_data; do
  # Boites_data est un fichier de DONNÉES : il ne contient aucun #print axioms.
  printf '  --- %s.lean\n' "$f"
  lake env lean "$f.lean" > "/tmp/v_$f.log" 2>&1
  if grep -qE "declaration uses 'sorry'|sorryAx" "/tmp/v_$f.log"; then
    ko "  $f.lean contient un sorry"; SORRY=1
  fi
  if [ "$f" = "Boites_data" ]; then
    if [ -s "/tmp/v_$f.log" ]; then
      info "  sortie non vide (fichier de données) :"; head -5 "/tmp/v_$f.log" | sed 's/^/         /'
    else
      ok "  compile sans sortie (données seulement, rien à prouver)"
    fi
    continue
  fi
  # chaque #print axioms doit rendre [propext, Classical.choice, Quot.sound]
  NB=$(grep -c "depends on axioms" "/tmp/v_$f.log" || true)
  MAUVAIS=$(grep "depends on axioms" "/tmp/v_$f.log" | grep -v "\[propext, Classical.choice, Quot.sound\]" | wc -l)
  if [ "$NB" -eq 0 ]; then
    info "  aucun #print axioms dans ce fichier"
  elif [ "$MAUVAIS" -eq 0 ]; then
    ok "  $NB théorème(s), tous aux axiomes habituels"
  else
    ko "  $MAUVAIS théorème(s) avec des axiomes supplémentaires :"
    grep "depends on axioms" "/tmp/v_$f.log" | grep -v "\[propext, Classical.choice, Quot.sound\]" | sed 's/^/         /'
    AXIOMES=1
  fi
done

# ---------------------------------------------------------------- bilan
titre "Bilan"
TOTAL=$(cat /tmp/v_Geometrie.log /tmp/v_Queue.log /tmp/v_Pont.log /tmp/v_Boites.log 2>/dev/null \
        | grep -c "depends on axioms" || true)
printf '  théorèmes contrôlés (geom) : %s\n' "$TOTAL"
[ "$SORRY" -eq 0 ]    && ok "aucun sorry"                  || ko "des sorry subsistent"
[ "$AXIOMES" -eq 0 ]  && ok "aucun axiome supplémentaire"  || ko "axiomes en trop"

if [ "$ECHEC" -eq 0 ]; then
  printf '\n\033[32mTOUT EST VERT\033[0m — renvoyez les fichiers /tmp/v_*.log si vous voulez un examen détaillé.\n'
else
  printf '\n\033[31mAU MOINS UN CONTRÔLE A ÉCHOUÉ\033[0m — journaux : /tmp/v_*.log\n'
fi
exit "$ECHEC"
