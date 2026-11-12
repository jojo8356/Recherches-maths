"""Tests de regression des moteurs, rejouables : python3 tests_moteurs.py

Ajoute apres l'audit du 3 novembre 2026, apres qu'un « second bug » annonce se soit revele
invérifiable faute d'historique. Chaque test compare a une reference independante.
"""
import random
import sys
sys.path.insert(0, '/home/user/dossiers/note')
sys.path.insert(0, '/home/user/dossiers/phase6')

import partition2
import coloriage
import echelle
import tangence


def brute_couleur(adj, k):
    n = len(adj)
    def rec(i, col):
        if i == n: return True
        for c in range(k):
            if all(col[j] != c for j in adj[i] if j < i):
                col[i] = c
                if rec(i + 1, col): return True
                col[i] = -1
        return False
    return rec(0, [-1] * n)


def brute_clique(adj):
    n = len(adj); best = [0]
    def rec(cand, k):
        if k + len(cand) <= best[0]: return
        if not cand:
            best[0] = max(best[0], k); return
        for v in sorted(cand):
            rec(cand & adj[v], k + 1)
            cand = cand - {v}
    rec(set(range(n)), 0)
    return best[0]


def verif_coloriage(adj, col):
    return all(col[u] != col[v] for u in range(len(adj)) for v in adj[u])


def graphe_aleatoire(rnd, nmin=6, nmax=11, kset=(2, 3)):
    n = rnd.randint(nmin, nmax); k = rnd.choice(kset); p = rnd.uniform(0.25, 0.6)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rnd.random() < p:
                adj[i].add(j); adj[j].add(i)
    return adj, k


def main(n=200):
    echecs = []
    rnd = random.Random(7)
    for _ in range(n):
        adj, k = graphe_aleatoire(rnd)
        r, col = partition2.k_color([set(a) for a in adj], k)
        if isinstance(r, list) and not verif_coloriage(adj, r):
            echecs.append("k_color a rendu un coloriage invalide")
        if isinstance(r, list) != brute_couleur(adj, k):
            echecs.append("k_color desaccorde avec la force brute")
    rnd = random.Random(11)
    for _ in range(n):
        adj, k = graphe_aleatoire(rnd)
        ok, col = coloriage.coloriable([set(a) for a in adj], k, retour_couleurs=True)
        if ok and not coloriage.valide(adj, col):
            echecs.append("coloriage.coloriable a rendu un coloriage invalide")
        if ok != brute_couleur(adj, k):
            echecs.append("coloriage.coloriable desaccorde avec la force brute")
    rnd = random.Random(3)
    for _ in range(n):
        adj, _ = graphe_aleatoire(rnd)
        adj = [set(a) for a in adj]
        w, cl = partition2.clique_max([set(a) for a in adj])
        if w != brute_clique(adj):
            echecs.append("clique_max desaccorde avec la force brute")
    # le calcul flottant doit retrouver le juge exact (corps Q(sqrt d))
    import json
    exact = json.load(open('/home/user/dossiers/note/exact_tangence.json'))
    for cle, ref in exact.items():
        nom, ds = cle.split('|')
        rho, th = {"hexagonal (60 deg)": (1.0, 60), "carre (90 deg)": (1.0, 90),
                   "rectangle 2:1 (90 deg)": (2.0, 90)}[nom]
        import fractions
        _, wl = tangence.omega_deux(rho, th, float(fractions.Fraction(ds)))
        if wl != ref:
            echecs.append(f"omega flottant {wl} != exact {ref} pour {cle}")
    if echecs:
        from collections import Counter
        print("ECHECS :", Counter(echecs))
        return 1
    print(f"tous les tests passent ({3*n} graphes aleatoires + {len(exact)} valeurs exactes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
