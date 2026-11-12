#!/usr/bin/env bash
# Vérifie les deux projets Lean du dossier Sokolov–Voronov.
#
#   bash dossiers/verifier.sh
#
# Ce que ce script contrôle, et que « build succeeded » ne dit PAS :
#  1. les deux projets compilent ;
#  2. aucun théorème ne dépend de `sorryAx` (Lean accepte `sorry` avec un simple
#     avertissement : le build passe quand même) ;
#  3. chaque théorème dont on interroge les axiomes n'a QUE propext, Classical.choice,
#     Quot.sound ;
#  4. les fichiers que `lake build` ne visite pas sont vérifiés QUAND MÊME, un par un ;
#  5. une sortie inattendue n'est jamais comptée comme un succès.
#
# HISTORIQUE DES DÉFAUTS DE CE SCRIPT (ils expliquent plusieurs de ses formes bizarres) :
#  * v1 comptait les théorèmes de `geom` en lisant les journaux de `lake env lean`. Or
#    `Boites.lean` échouait (« unknown module prefix 'Queue' »), donc son journal ne
#    contenait aucun axiome — et le script concluait « aucun axiome supplémentaire »
#    sur un fichier qu'il n'avait pas pu lire. Un faux négatif silencieux.
#  * v1 ne construisait que `defaultTargets = ["Geometrie"]` : `lake build` s'arrêtait à
#    Geometrie, et ni Queue, ni Pont, ni Boites n'étaient compilés.
#  * v1 affichait « TOUT EST VERT » alors que Boites.lean était en erreur.
# Le remède : `lake env lean` file par file, l'échec d'un fichier est un ÉCHEC, et le
# bilan additionne les théorèmes RÉELLEMENT VÉRIFIÉS, jamais annoncés.

set -u

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECHEC=0
THEOREMES=0

titre() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
ok()    { printf '  \033[32mOK\033[0m    %s\n' "$*"; }
ko()    { printf '  \033[31mÉCHEC\033[0m %s\n' "$*"; ECHEC=1; }
info()  { printf '  ..    %s\n' "$*"; }

# ---------------------------------------------------------------- branche
titre "Branche"
BRANCHE="$(git -C "$RACINE" branch --show-current 2>/dev/null || echo '(inconnue)')"
info "branche : $BRANCHE"
if [ "$BRANCHE" = "main" ]; then
  ko "vous êtes sur main, qui ne contient pas le travail récent (gestes 39-41).
      Le lakefile y est encore celui du bac à sable (/var/tmp) et Boites_data n'y est pas déclaré.
      Basculez d'abord :  git checkout arena/dfb03fac-recherches-maths"
  exit 1
fi

# ---------------------------------------------------------------- prérequis
titre "Prérequis"
if ! command -v lake >/dev/null 2>&1; then
  ko "lake introuvable. Installer elan :
      curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
      source \"\$HOME/.elan/env\""
  exit 1
fi
ok "lake : $(command -v lake)"
lake --version 2>/dev/null | head -1 | sed 's/^/        /'

# ---------------------------------------------------------------- cohérence lakefile
# Ce contrôle est né de TROIS bugs identiques : un .lean présent dans le dossier mais absent
# des [[lean_lib]]. `lake build` ne le construit alors jamais, et `lake env lean` échoue sur
# « unknown module prefix ». Ont été dans ce cas : Boites_data, Axiomes, puis Pont (dans
# dossiers/lean) — ce dernier invisible de Lake pendant des séances entières.
titre "Cohérence : chaque .lean du dossier est-il une cible déclarée ?"
for dossier in lean geom; do
  dir="$RACINE/$dossier"
  [ -d "$dir" ] || continue
  declares=$(python3 - "$dir/lakefile.toml" <<'PY'
import sys, tomllib
d = tomllib.load(open(sys.argv[1], "rb"))
print(" ".join(l["name"] for l in d.get("lean_lib", [])))
PY
)
  manquants=""
  for f in "$dir"/*.lean; do
    [ -e "$f" ] || continue
    m="$(basename "$f" .lean)"
    case " $declares " in *" $m "*) ;; *) manquants="$manquants $m" ;; esac
  done
  if [ -z "$manquants" ]; then
    ok "  $dossier : tous les .lean sont déclarés ($(echo $declares | wc -w) cibles)"
  else
    ko "  $dossier : fichier(s) présent(s) mais non déclaré(s) dans lakefile.toml :"
    printf '         %s\n' $manquants
    printf '         lake build ne les construira jamais et lake env lean échouera.\n'
    printf '         (Votre copie est peut-être en retard : git pull)\n'
  fi
done

# ---------------------------------------------------------------- projet sans dépendance
titre "dossiers/lean — noyau pur, aucune dépendance (~30 s)"
cd "$RACINE/lean" || { ko "dossier lean absent"; exit 1; }
info "toolchain épinglée : $(cat lean-toolchain)"
lake build > /tmp/v_lean.log 2>&1
if grep -q "Build completed successfully" /tmp/v_lean.log; then
  ok "build"
else
  ko "build (voir /tmp/v_lean.log)"; tail -5 /tmp/v_lean.log | sed 's/^/        /'
fi

# ---------------------------------------------------------------- projet Mathlib
titre "dossiers/geom — Mathlib (long la première fois)"
cd "$RACINE/geom" || { ko "dossier geom absent"; exit 1; }
info "toolchain épinglée : $(cat lean-toolchain)"
if [ ! -d .lake/packages/mathlib ]; then
  info "dépendances absentes : lake update"
  lake update > /tmp/v_update.log 2>&1
fi
if [ ! -d .lake/packages/mathlib/.lake/build/lib/lean ]; then
  info "cache Mathlib absent : lake exe cache get (évite des heures de compilation)"
  lake exe cache get > /tmp/v_cache.log 2>&1
fi
info "build de TOUTES les cibles (defaultTargets ne contient que Geometrie)"
lake build Geometrie Pont Queue Boites Boites_data > /tmp/v_geom.log 2>&1
if grep -q "Build completed successfully" /tmp/v_geom.log; then
  ok "build"
else
  ko "build (voir /tmp/v_geom.log)"; tail -8 /tmp/v_geom.log | sed 's/^/        /'
fi

# ---------------------------------------------------------------- contrôles par fichier
titre "Contrôles : axiomes, absence de sorry, et échec de lecture"
verifie_fichier() {           # $1 = dossier, $2 = nom sans .lean
  local fichier="$2.lean" journal="/tmp/v_$2.log" note="${3:-}"
  printf '  --- %s.lean%s\n' "$2" "${note:+  ($note)}"
  local statut=0
  # CONSTRUIRE LA CIBLE D'ABORD. `lake env lean X.lean` ne met pas le lib/lean de notre
  # propre paquet dans LEAN_PATH tant qu'il est vide : sur un dépôt fraîchement cloné, ou
  # pour un module jamais construit, cela donne « unknown module prefix '<Module>' ».
  # `lake build <Module>` construit les .olean ET les met dans le chemin. C'est le remède,
  # et il vaut pour Boites, Boites_data et Axiomes comme pour les autres.
  ( cd "$1" && lake build "$2" ) > "/tmp/v_build_$2.log" 2>&1 || statut=$?
  if [ "$statut" -ne 0 ]; then
    ko "  $2 : 'lake build $2' a échoué (voir /tmp/v_build_$2.log) :"
    grep -E "error:" "/tmp/v_build_$2.log" | head -3 | sed 's/^/         /'
    return
  fi
  ( cd "$1" && lake env lean "$fichier" ) > "$journal" 2>&1 || statut=$?

  # 1a. code de sortie non nul : `lake env lean` a échoué, même sans ligne « error: »
  #     (c'est le cas, par exemple, si le fichier n'existe pas).
  if [ "$statut" -ne 0 ] && ! grep -qE "^[^ ]*:[0-9]+:[0-9]+: error:" "$journal"; then
    ko "  $2.lean : lake env lean a rendu le code $statut :"
    tail -3 "$journal" | sed 's/^/         /'
    return
  fi
  # 1b. une ERREUR de lecture/compilation est un échec, quoi qu'on trouve ensuite.
  if grep -qE "^[^ ]*:[0-9]+:[0-9]+: error:" "$journal"; then
    ko "  $2.lean ne compile pas :"
    grep -E "error:" "$journal" | head -3 | sed 's/^/         /'
    return
  fi
  # 2. sorry
  if grep -qE "declaration uses 'sorry'|sorryAx" "$journal"; then
    ko "  $2.lean contient un sorry"; return
  fi
  # 3. axiomes
  local nb mauvais
  nb=$(grep -c "depends on axioms" "$journal" || true)
  if [ "$nb" -eq 0 ]; then
    # Un fichier sans #print axioms est normal (données) — mais on le DIT, sans le
    # compter comme vérifié.
    info "  compile, aucun théorème interrogé (pas de #print axioms)"
    return
  fi
  mauvais=$(grep "depends on axioms" "$journal" | grep -v "\[propext, Classical.choice, Quot.sound\]" | wc -l)
  if [ "$mauvais" -eq 0 ]; then
    ok "  $nb théorème(s), axiomes habituels"
    THEOREMES=$((THEOREMES + nb))
  else
    ko "  $mauvais théorème(s) avec des axiomes supplémentaires :"
    grep "depends on axioms" "$journal" | grep -v "\[propext, Classical.choice, Quot.sound\]" | sed 's/^/         /'
  fi
}

vermifuge() {   # compte les `theorem` déclarés, pour dire ce qui n'est pas interrogé
  grep -c '^theorem' "$1/$2.lean" 2>/dev/null || echo 0
}

# --- geom
for f in Geometrie Queue Pont Boites; do
  verifie_fichier "$RACINE/geom" "$f"
  declares=$(vermifuge "$RACINE/geom" "$f")
  interroges=$(grep -c "depends on axioms" "/tmp/v_$f.log" || true)
  if [ "${declares:-0}" -gt "${interroges:-0}" ]; then
    info "  $f.lean : $declares théorèmes déclarés, $interroges interrogés par #print axioms"
  fi
done
verifie_fichier "$RACINE/geom" "Boites_data" "données : bornes, seuil T, clique"

# --- lean (noyau pur) : les fichiers ne sont pas tous dans defaultTargets
for f in Plafond T8; do
  verifie_fichier "$RACINE/lean" "$f"
done
# Pont.lean n'est pas une lean_lib : il est vérifié par `lake env lean`, pas par `lake build`.
info "vérification directe de dossiers/lean/Pont.lean :"
verifie_fichier "$RACINE/lean" "Pont" "noyau pur"

# ---------------------------------------------------------------- audit complet des axiomes
titre "Audit complet : les 70 théorèmes, un #print axioms chacun"
# Les #print axioms dispersés dans les preuves n'interrogent qu'une partie des théorèmes
# (Queue.lean : 5 sur 28). Axiomes.lean, généré par note/gen_axiomes.py, les interroge TOUS.
for dossier in geom lean; do
  journal="/tmp/v_axiomes_$dossier.log"
  # même règle : construire la cible avant de la lire
  ( cd "$RACINE/$dossier" && lake build Axiomes ) > "/tmp/v_build_axiomes_$dossier.log" 2>&1
  ( cd "$RACINE/$dossier" && lake env lean Axiomes.lean ) > "$journal" 2>&1
  nb=$(grep -c "depends on axioms" "$journal" || true)
  mauvais=$(grep "depends on axioms" "$journal" | grep -vE "\[(propext, )?(Classical.choice, )?(Quot.sound)\]" | wc -l)
  erreur=$(grep -cE "^[^ ]*:[0-9]+:[0-9]+: error:" "$journal" || true)
  if [ "${erreur:-0}" -gt 0 ]; then
    ko "  $dossier/Axiomes.lean ne compile pas :"; grep -E "error:" "$journal" | head -3 | sed 's/^/         /'
  elif [ "$nb" -eq 0 ]; then
    ko "  $dossier/Axiomes.lean : aucun axiome rendu (fichier non lu ?)"
  elif [ "$mauvais" -eq 0 ]; then
    ok "  $dossier : $nb théorème(s), tous aux axiomes habituels"
    THEOREMES=$((THEOREMES + nb))
  else
    ko "  $dossier : $mauvais théorème(s) hors des axiomes habituels :"
    grep "depends on axioms" "$journal" | grep -vE "\[(propext, )?(Classical.choice, )?(Quot.sound)\]" | sed 's/^/         /'
  fi
done

# ---------------------------------------------------------------- bilan
titre "Bilan"
printf '  théorèmes contrôlés, geom + lean : %s\n' "$THEOREMES"
if [ "$ECHEC" -eq 0 ]; then
  printf '\n\033[32mTOUS LES CONTRÔLES PASSENT\033[0m\n'
else
  printf '\n\033[31mAU MOINS UN CONTRÔLE A ÉCHOUÉ\033[0m — journaux : /tmp/v_*.log\n'
fi
printf 'Journaux : /tmp/v_*.log\n'
exit "$ECHEC"
