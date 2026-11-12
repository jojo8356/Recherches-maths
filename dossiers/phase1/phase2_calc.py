import math, json
SQ3=math.sqrt(3)

print("="*66); print("P1 — MODÈLE DU COÛT : combien de sommets pour la couleur suivante ?"); print("="*66)
n={2:2,3:3,4:7,5:509}
ratio={k:n[k]/n[k-1] for k in (3,4,5)}
print("tailles connues :",n)
print("ratios successifs n_k/n_{k-1} :",{k:round(v,3) for k,v in ratio.items()})
rr=ratio[5]/ratio[4]
print(f"rapport des ratios (k=4 -> k=5) : {rr:.1f}")
models={}
models['M1 ratio constant (72,7)']=n[5]*ratio[5]
models['M2 le ratio croît comme au cran précédent']=n[5]*ratio[5]*rr
ln=[math.log(n[k]) for k in range(2,6)]
ll=[math.log(ln[i]) for i in range(4)]
slope=((ll[3]-ll[2])+(ll[2]-ll[1]))/2
models['M3 double exponentielle (log log linéaire)']=math.exp(math.exp(ll[3]+slope))
for k,v in models.items(): print(f"   {k:48s} -> n_6 ≈ {v:,.0f}")
lo,hi=min(models.values()),max(models.values())
print(f"\nPRÉDICTION P1 : un témoin 6-chromatique, s'il existe, a très probablement")
print(f"   n_6 ≳ 10^5 sommets (fourchette des modèles : {lo:,.0f} à {hi:,.0f})")
print(f"   soit ≥ {lo/n[5]:.0f}× le plus gros témoin connu. À comparer : le record est passé")
print("   de 1581 à 509 en 3 ans d'efforts intensifs (Polymath16).")

print(); print("="*66); print("P2 — TEST DE MA PROPRE IDÉE : la densité suffit-elle ?"); print("="*66)
# idée testée : borner la densité d'une classe sans distance unité (delta_max),
# et conclure que delta_max < 1/6 tuerait tout 6-coloriage mesurable.
# construction : disques de rayon r<1/2 aux sommets d'un réseau hexagonal de pas L>1+2r
def densite(r,L): return math.pi*r*r/(SQ3/2*L*L)
best=(0,None)
for i in range(1,4000):
    r=0.4999*i/4000
    L=max(1+2*r+1e-9, 2*r+1e-9)
    if r>0.5: continue
    d=densite(r,L)
    if d>best[0]: best=(d,r,L)
r=0.4999; L=1+2*r+1e-9
print(f"construction testée : disques de rayon r={r:.4f} (diamètre {2*r:.4f} < 1)")
print(f"   centres sur réseau hexagonal de pas L={L:.4f} (= 1 + 2r, donc écart minimal entre disques > 1)")
print(f"   -> aucun couple à distance exactement 1 (dans un disque : diamètre < 1 ; entre disques : min > 1)")
print(f"   densité obtenue : {densite(r,L):.4f}")
print(f"   supremum théorique (r -> 1/2, L -> 2) : pi/(8*sqrt(3)) = {math.pi/(8*SQ3):.4f}")
delta=math.pi/(8*SQ3)
print(f"\n   comparaison : 1/6 = {1/6:.4f} et 1/7 = {1/7:.4f}")
print(f"   delta_max >= {delta:.4f} > 1/6 = {1/6:.4f}  =>  LA ROUTE PAR LA DENSITÉ EST MORTE.")
print("   (un 6-coloriage pourrait avoir des classes de densité > 1/6 : rien ne l'interdit)")

# densité exacte d'une classe du 7-coloriage
print(f"\nnéanmoins : le 7-coloriage a des classes de densité EXACTEMENT 1/7 = {1/7:.4f}")
print(f"   (couleur(q,r)=(q+3r) mod 7 est un morphisme Z^2 -> Z/7 : chaque classe est un translaté")
print(f"    du noyau, réseau d'indice 7 -> densité 1/7 par périodicité)")
print(f"   inefficacité d'une classe du 7-coloriage : {1/7:.4f} / {delta:.4f} = {1/7/delta:.2f} de l'optimum individuel")

print(); print("="*66); print("P2bis — CE QUE LA DENSITÉ DIT QUAND MÊME"); print("="*66)
print("Un coloriage en k classes mesurables est une PARTITION : les densités somment à 1.")
print("Comme une classe seule peut atteindre 0,2267 > 1/6, aucune borne de densité ne")
print("peut interdire k=6. L'obstruction n'est donc pas la taille des classes mais leur")
print("COMPATIBILITÉ (recouvrir le complément). Le problème est un problème de recouvrement.")

# conséquence : un 6-coloriage, s'il existe, doit être déséquilibré
print("\nconséquence heuristique : un 6-coloriage devrait avoir des classes très inégales")
print(f"   ex. 5 classes à {delta:.4f} + 1 classe à {1-5*delta:.4f} — soit une classe résiduelle")
print(f"   de densité {1-5*delta:.4f}, très inférieure à la moyenne 1/6 = {1/6:.4f}.")
print("   Or une classe de densité quasi nulle qui doit boucher tous les trous d'un motif")
print("   hexagonal est une structure très contrainte : c'est là que je placerais le verrou.")

json.dump({'n':n,'models':models,'delta_lb':delta,'dens7':1/7},open('res_phase2.json','w'))
