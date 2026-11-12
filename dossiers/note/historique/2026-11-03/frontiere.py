import sys,json; sys.path.insert(0,'.')
from balayage import omega_reseau
def omega(rho,th): return omega_reseau(rho,th,R=3)
print("Frontiere du plateau omega=7 le long de rho = constante (bisection, R=3)")
print("(omega saute de 7 a 8 en franchissant la frontiere)\n")
OUT={}
for rho in (1.0,1.2,1.4,1.6,1.8,1.9,1.95):
    # on cherche la plus grande valeur de theta (proche de 90) ou omega reste 7
    lo,hi=60.0,90.0
    if omega(rho,lo)!=7: 
        print(f"  rho={rho}: omega(60)={omega(rho,lo)}, pas de plateau depuis 60 deg"); continue
    if omega(rho,hi)==7:
        print(f"  rho={rho}: plateau jusqu'a 90 deg (carre) -> aucune frontiere avant 90"); OUT[rho]=None; continue
    for _ in range(40):
        mid=(lo+hi)/2
        if omega(rho,mid)==7: lo=mid
        else: hi=mid
    OUT[rho]=lo
    print(f"  rho={rho:.2f} : omega = 7 jusqu'a theta = {lo:.6f} deg (omega(lo+1e-6)={omega(rho,lo+1e-6)})")
json.dump({str(k):v for k,v in OUT.items()},open('frontiere.json','w'))
print("\nverification de la monotonie : la frontiere recule quand rho augmente ?")
print("  ",{k:(round(v,4) if v else None) for k,v in OUT.items()})
