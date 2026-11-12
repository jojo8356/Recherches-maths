import math
SQ3=math.sqrt(3)

print("="*70)
print("1. LE PLAFOND D'UNE METHODE 'UNE CLASSE A LA FOIS'")
print("="*70)
print("""
Un argument qui n'utilise d'une classe de couleur que deux faits
  (i) elle est mesurable,  (ii) elle ne contient aucun couple à distance 1
ne peut connaître qu'une chose : sa densité maximale delta_max.
Si chaque classe a une densité <= delta_max, alors k classes couvrent
au plus une densité k*delta_max. Un tel argument ne peut donc exclure
k = plafond(1/delta_max). Autrement dit il démontre au mieux chi >= 1/delta_max.
""")
delta=math.pi/(8*SQ3)
print(f"or la phase 2 a construit une classe sans distance 1 de densité pi/(8*sqrt3) = {delta:.4f}")
print(f"=> toute borne de ce type est plafonnée à 1/{delta:.4f} = {1/delta:.3f}  ->  au mieux chi >= 5")
print(f"=> pour démontrer chi >= 6 il faudrait delta_max < 1/5 = 0,2000, soit {100*(1-delta/0.2):.0f} % SOUS la valeur déjà atteinte.")

print()
print("="*70)
print("2. LA CONSTRUCTION EST-ELLE OPTIMALE DANS SA FAMILLE ?")
print("="*70)
print("Lemme : un ensemble sans distance 1 qui est une réunion de blobs bornés est")
print("une famille de blobs de diamètre < 1, deux à deux à distance > 1.")
print("(sinon la distance entre deux blobs traverse 1, et par continuité il existe")
print(" un couple à distance exactement 1).")
print()
def densite(forme,r,s,reseau):
    if reseau=='hex': aire_cellule=SQ3/2*s*s
    else: aire_cellule=s*s
    if forme=='disque': a=math.pi*r*r; diam=2*r
    elif forme=='hexagone': a=(3*SQ3/2)*r*r; diam=2*r
    else: a=4*r*r; diam=2*r*math.sqrt(2)   # carré de demi-côté r
    return a/aire_cellule, diam
best={}
for reseau in ('hex','carre'):
    for forme in ('disque','hexagone','carre'):
        bestv=(0,None)
        for i in range(1,4000):
            r=0.7*i/4000
            d,_=densite(forme,r,2.0,reseau)
            if _>=1: continue
            # pas minimal : séparation > 1 entre blobs
            s_min = (1+2*r) if forme!='carre' else (1+2*r*math.sqrt(2)/math.sqrt(2)*1.0)
            s=max(s_min, 2*r+1.0)
            d,_=densite(forme,r,s,reseau)
            if d>bestv[0]: bestv=(d,(round(r,4),round(s,4)))
        best[(reseau,forme)]=bestv
        print(f"   réseau {reseau:6s} + blob {forme:9s} : densité max = {bestv[0]:.4f}  (r={bestv[1][0]}, pas={bestv[1][1]})")
gagnant=max(best.items(),key=lambda kv:kv[1][0])
print(f"\n   meilleur : {gagnant[0]} -> {gagnant[1][0]:.4f}")
print(f"   valeur théorique (r -> 1/2, pas -> 2) : pi/(8*sqrt3) = {math.pi/(8*SQ3):.4f}")
print("   le disque gagne par l'inégalité isodiamétrique ; l'hexagone et le carré font moins bien.")
print()
print("="*70)
print("3. COHERENCE AVEC LA LITTERATURE")
print("="*70)
print("La meilleure borne connue dans le cas mesurable est 5 (Falconer 1981).")
print(f"Le plafond de la méthode est {1/delta:.2f} -> 5.")
print("=> la méthode est SATURÉE : ce n'est pas qu'on n'a pas trouvé le bon noyau,")
print("   c'est qu'aucun noyau ne peut dépasser 5. D'où 40 ans sans progrès.")
