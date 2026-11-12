import math
from fractions import Fraction as Fr
exec(open('exact.py').read().split("print(\"tests")[0])   # récupère A, d2, hexpatch, rot30_scale

R=3
base=hexpatch(R)
copy=[rot30_scale(p) for p in base]
allp=base+copy
uniq=list({p for p in allp})
print(f"base={len(base)} copy={len(copy)} total={len(allp)} unique={len(uniq)} -> doublons={len(allp)-len(uniq)}")
dups=[p for p in set(allp) if allp.count(p)>1]
def tofloat(p): return (float(p[0].a)+float(p[0].b)*math.sqrt(3), float(p[1].a)+float(p[1].b)*math.sqrt(3))
print("exemples de points dupliqués :",[ (round(tofloat(p)[0],4),round(tofloat(p)[1],4)) for p in dups[:6]])

# version flottante reconstruite à l'identique
SQ3=math.sqrt(3)
def hexpatch_f(R):
    return [(q+r/2, r*SQ3/2) for q in range(-R,R+1) for r in range(-R,R+1) if max(abs(q),abs(r),abs(q+r))<=R]
def rotf(p):
    s=1/SQ3; th=math.pi/6; c,si=math.cos(th),math.sin(th)
    return (s*(c*p[0]-si*p[1]), s*(si*p[0]+c*p[1]))
Pf=hexpatch_f(R)+[rotf(p) for p in hexpatch_f(R)]
Uf=[tofloat(p) for p in uniq]
print(f"\npoints flottants (sans dédoublonnage)={len(Pf)} | points exacts convertis={len(Uf)}")
# les deux ensembles coïncident-ils ?
def key(p): return (round(p[0],9),round(p[1],9))
print("ensembles égaux :", set(map(key,Pf))==set(map(key,Uf)))

# arêtes flottantes : lesquelles ne sont PAS exactement unité ?
bad=[]; good=0
tol=1e-7
for i in range(len(Uf)):
    for j in range(i+1,len(Uf)):
        dx=Uf[i][0]-Uf[j][0]; dy=Uf[i][1]-Uf[j][1]; dd=dx*dx+dy*dy
        if abs(dd-1.0)<tol:
            ex = d2(uniq[i],uniq[j])
            if ex.a==1 and ex.b==0: good+=1
            else: bad.append((i,j,round(dd,12),ex))
print(f"paires à |d2-1|<1e-7 : {good+bad} dont exactes={good}, fausses={len(bad)}")
for b in bad[:8]: print("   fausse arête : d2 flottant =",b[2]," d2 exact =",b[3])
