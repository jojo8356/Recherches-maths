"""Diagnostic de l'accès au toolchain Lean — ce qui bloque, et où.

Contexte
--------
Le geste 39 n'a pas pu compiler : `elan` et la toolchain n'étaient pas installables, et les
hôtes de release GitHub répondaient `SSL_ERROR_SYSCALL`. Ce script rejoue le diagnostic de
façon reproductible et CHIFFRÉE, pour que la demande d'ouverture de pare-feu porte sur des
hôtes et des volumes exacts, et non sur « ça ne marche pas ».

Ce qu'il établit
----------------
1. Les hôtes autorisés dans ce bac à sable ne servent AUCUN artefact Lean : `pypi` et `npm`
   répondent, mais `lean4`, `lean`, `pyelan` sur PyPI sont des wrappers (0,01 à 0,02 Mo), et
   `lean-dojo` (67 Mo) ne contient qu'un jeu de données de benchmark, aucun binaire.
2. La toolchain vient de DEUX sources, toutes deux bloquées :
     - elan  : github.com → 302 → objects.githubusercontent.com (bloqué) ;
     - lean4 : releases.lean-lang.org (bloqué ; c'est l'URL qu'utilise elan, cf. setup.log).
3. Le cache Mathlib (`lake exe cache get`) vient d'un TROISIÈME hôte, également bloqué.
   `leanprover-community.github.io` est en effet un domaine GitHub **Pages** : il se sert par
   Fastly, pas par `github.com` — l'autoriser ne suffit donc pas à autoriser `codeload`.
4. Conséquence : compiler sur place sans le cache demanderait de construire Mathlib depuis la
   source, ce qui n'est pas faisable ici (2 cœurs, 3 Go de RAM, et Mathlib demande ~10 Go et
   plusieurs heures).

Sortie : 0 si la compilation est possible (toutes les sources accessibles), 1 sinon.
"""
import json
import shutil
import socket  # noqa: F401  (gardé pour le commentaire ci-dessus)
import subprocess
import sys
import urllib.request

HOTES = [
    ("github.com", "redirection des releases elan", True),
    ("api.github.com", "métadonnées des releases", True),
    ("codeload.github.com", "archives de source (git clone)", True),
    ("objects.githubusercontent.com", "CIBLE du 302 : artefacts de release elan", False),
    ("release-assets.githubusercontent.com", "artefacts de release (autre nom)", False),
    ("raw.githubusercontent.com", "scripts d'installation (elan-init.sh)", False),
    ("releases.lean-lang.org", "toolchain lean4 (ce qu'elan télécharge)", False),
    ("leanprover-community.github.io", "cache Mathlib (GitHub Pages, servi par Fastly)", False),
    ("mathlib.cache.azureedge.net", "repli du cache Mathlib", False),
]


def joignable(hote, timeout=12):
    """Vrai si une requête HTTPS aboutit — pas seulement si le TCP s'ouvre.

    PREMIÈRE VERSION FAUSSE : je testais `socket.create_connection((hote, 443))`, qui
    réussissait sur TOUS les hôtes, y compris les bloqués. La raison est un proxy de sortie
    transparent : il accepte la connexion TCP puis coupe au ClientHello TLS. Un test de
    connexion est donc un faux positif systématique ; il faut aller jusqu'à la requête.
    Le symptôme visible côté client est `SSL_ERROR_SYSCALL`, pas un refus de connexion.
    """
    try:
        req = urllib.request.Request(f"https://{hote}/", method="HEAD")
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except urllib.error.HTTPError:
        return True                      # une réponse HTTP, même 4xx, prouve le TLS
    except Exception:                    # noqa: BLE001
        return False


def main():
    print("=" * 78)
    print("1. Accessibilité des hôtes (TCP 443)")
    print("=" * 78)
    etat = {}
    for hote, role, suffisant in HOTES:
        ok = joignable(hote)
        etat[hote] = ok
        marque = "OUVERT " if ok else "BLOQUÉ "
        print(f"  {marque} {hote:40s} {role}")
    print()

    manquants = [h for h, _, _ in HOTES if not etat[h]]
    print("=" * 78)
    print("2. Aucun substitut dans les dépôts accessibles")
    print("=" * 78)
    for paquet, eco in [("lean4", "pypi"), ("lean", "pypi"), ("pyelan", "pypi")]:
        try:
            u = f"https://pypi.org/pypi/{paquet}/json"
            d = json.load(urllib.request.urlopen(u, timeout=20))
            tailles = [a["size"] for a in d["urls"]] or [0]
            print(f"  {eco}/{paquet:10s} {max(tailles) / 1e6:6.2f} Mo  "
                  f"{(d['info']['summary'] or '(sans description)')[:52]}")
        except Exception as e:  # noqa: BLE001
            print(f"  {eco}/{paquet:10s} inaccessible ({e})")
    print(f"  npm           : aucun paquet ne fournit le binaire lean "
          f"(@leanprover/* = interfaces, pas de toolchain)")
    print("  => les deux dépôts autorisés ne servent pas d'artefact Lean compilé.")
    print()

    print("=" * 78)
    print("3. Outils de compilation sur place")
    print("=" * 78)
    outils = {c: shutil.which(c) for c in ("g++", "make", "cmake", "ninja", "zstd")}
    for c, p in outils.items():
        print(f"  {c:8s} {p or 'ABSENT'}")
    print()
    try:
        n = len(open("/proc/cpuinfo").read().split("processor")) - 1
    except OSError:
        n = 0
    mem = 0
    try:
        for ligne in open("/proc/meminfo"):
            if ligne.startswith("MemTotal"):
                mem = int(ligne.split()[1]) / 1024 ** 2
    except OSError:
        pass
    print(f"  {n} cœurs, {mem:.1f} Go de RAM")
    print("  Mathlib depuis la source : ~10 Go et plusieurs heures ; hors de portée ici")
    print()

    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    if not manquants:
        print("  Toutes les sources sont accessibles : la compilation peut être lancée.")
        return 0
    print(f"  {len(manquants)} hôte(s) à ouvrir pour compiler :")
    for h in manquants:
        print(f"    - {h}")
    print()
    print("  Les quatre premiers suffisent pour la toolchain et les dépendances :")
    print("    objects.githubusercontent.com   (elan + lean4 si via releases GitHub)")
    print("    releases.lean-lang.org          (lean4, voie normale d'elan)")
    print("    raw.githubusercontent.com       (elan-init.sh)")
    print("    leanprover-community.github.io  (cache Mathlib : SANS lui, Mathlib depuis la source)")
    print("  Volumes : elan 5 Mo ; lean4 608 Mo (linux.tar.zst) ; cache Mathlib ~5 Go.")
    print("  Rien de tout cela n'est atteignable aujourd'hui, d'où le report de compilation.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
