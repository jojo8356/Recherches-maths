"""Un pavage reticulaire est-il 6-coloriable ?

Le graphe de conflit d'un pavage de Voronoi de reseau est un graphe de Cayley de Z^2 :
la cellule (i,j) est en conflit avec (i',j') ssi (i'-i, j'-j) appartient a l'anneau E
calcule par echelle.graphe_echelle. Un coloriage periodique de periode M (sous-reseau
d'indice m) est un coloriage du graphe quotient Z^2/M.

On teste donc, pour tous les sous-reseaux d'indice m <= MMAX, si le quotient est
6-coloriable. Si l'un l'est, on tient un 6-coloriage explicite du plan.
"""
import math
import sys

import echelle


def anneau(rho, thd, delta, convention="large"):
    """E = ensemble des differences en conflit avec la cellule d'indice 0.

    convention="large"  : tangence exacte comptee comme conflit (defaut, valeurs publiees)
    convention="strict" : tangence non comptee -> moins d'aretes, coloriage plus facile ;
                          c'est le test le plus defavorable a nos conclusions negatives.
    """
    import tangence
    P, b1, b2 = echelle.reseau_unite(rho, thd)
    offsets, adj = tangence.adjacence(rho, thd, delta, convention)
    E = {offsets[i] for i in adj[0]}
    return P, b1, b2, E, adj, offsets


def sous_reseaux(m):
    """Sous-reseaux d'indice m de Z^2, sous forme de generateurs (a,b),(0,c)."""
    out = []
    for a in range(1, m + 1):
        if m % a:
            continue
        c = m // a
        for b in range(a):
            out.append((a, b, c))
    return out


def quotient(E, a, b, c):
    """Graphe quotient Z^2/M, M engendre par (a,b) et (0,c).

    Renvoie (adjacence, boucle). Une BOUCLE signifie qu'une classe de couleur
    contient deux cellules en conflit : le coloriage est alors impossible, quelle que
    soit la couleur. Ne jamais escamoter les boucles (c'etait le bug du premier jet)."""
    m = a * c
    # representatives canoniques : classes de (i,j) ; on indexe par (i mod a, j mod c)
    # avec la relation (i,j) ~ (i + k*a, j + k*b + l*c)
    def cle(i, j):
        # forme normale : i dans [0,a), j dans [0,c)
        k = (i - (i % a)) // a
        jj = (j - k * b) % c
        return (i % a) * c + jj

    adj = [set() for _ in range(m)]
    boucle = False
    for (i, j) in E:
        for u in range(m):
            iu, ju = u // c, u % c
            v = cle(iu + i, ju + j)
            if v == u:
                boucle = True
            else:
                adj[u].add(v)
                adj[v].add(u)
    return adj, boucle


def coloriable(adj, k=6, retour_couleurs=False):
    """k-colorabilite exacte (DSATUR + retour arriere).

    Le point delicat : a chaque echec on DEFait l'affectation. Un backtracking qui
    laisse des couleurs derriere lui peut annoncer un coloriage inexistant (bug du
    premier jet, attrape par une verification directe : 11 409 conflits monochromes)."""
    n = len(adj)
    coul = [-1] * n

    def rec():
        best, bs, bd = None, -1, -1
        for v in range(n):
            if coul[v] >= 0:
                continue
            s = len({coul[u] for u in adj[v] if coul[u] >= 0})
            if (s, len(adj[v])) > (bs, bd):
                best, bs, bd = v, s, len(adj[v])
        if best is None:
            return True
        utilises = {coul[u] for u in adj[best] if coul[u] >= 0}
        for c in range(k):
            if c in utilises:
                continue
            coul[best] = c
            if rec():
                return True
            coul[best] = -1          # <= la ligne qui manquait
        return False

    ok = rec()
    return (ok, list(coul)) if retour_couleurs else ok


def valide(adj, coul):
    """Verifie qu'un coloriage est propre (aucune arete monochrome)."""
    return all(coul[u] != coul[v] for u in range(len(adj)) for v in adj[u])


def chercher(rho, thd, delta, mmax=24, verbose=True, convention="large"):
    P, b1, b2, E, adj, offsets = anneau(rho, thd, delta, convention)
    if verbose:
        print(f"rho={rho} theta={thd} delta={delta} : |E| = {len(E)} differences en conflit")
    nb = 0
    for m in range(6, mmax + 1):
        for (a, b, c) in sous_reseaux(m):
            g, boucle = quotient(E, a, b, c)
            if boucle:
                continue
            nb += 1
            oki, cg = coloriable(g, 6, retour_couleurs=True)
            if oki and not valide(g, cg):
                raise AssertionError("coloriage invalide : le backtracking est casse")
            if oki:
                if verbose:
                    print(f"  6-COLORIAGE TROUVE : indice {m}, sous-reseau (a,b,c)=({a},{b},{c})")
                return (True, m, (a, b, c), g)
    if verbose:
        print(f"  aucun 6-coloriage : {nb} sous-reseaux sans boucle testes, "
              f"tous de nombre chromatique >= 7")
    return (False, None, None, None)


if __name__ == "__main__":
    cas = [(2.0, 90.0, 0.78), (1.9375, 90.0, 0.78), (2.0, 87.0, 0.78),
           (1.0, 60.0, 0.45), (1.5, 75.0, 0.70)]
    for (rho, th, d) in cas:
        chercher(rho, th, d)
