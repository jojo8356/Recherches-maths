import math
# --- J0 par série, puis zéros par bissection ---
def J0(x, N=60):
    t=1.0; s=1.0; k=1
    while k<N:
        t*= -(x*x/4)/(k*k); s+=t
        if abs(t)<1e-18*abs(s): break
        k+=1
    return s
print("J0(0) =",J0(0.0),"  J0(2) =",J0(2.0),"  J0(4) =",J0(4.0))
zeros=[]
prev=0.5; fp=J0(prev)
x=0.6
while len(zeros)<6 and x<25:
    f=J0(x)
    if f*fp<0:
        a,b=prev,x
        for _ in range(200):
            m=(a+b)/2
            if J0(a)*J0(m)<=0: b=m
            else: a=m
        zeros.append((a+b)/2)
    prev,fp=x,f; x+=0.05
print("zéros positifs de J0 :", [round(z,4) for z in zeros])
print("signes de la transformée de Fourier du cercle unité (2*pi*J0(2*pi*r)) :")
for r in (0.1,0.5,0.9,1.5,2.5,3.5):
    v=2*math.pi*J0(2*math.pi*r)
    print(f"   rayon de fréquence {r:4.1f} -> J0 = {v:+.3f}  ({'positif' if v>0 else 'NÉGATIF'})")
print("\nConséquence : la contrainte 'pas de distance 1' s'écrit <f,f*sig> = integrale |f_hat|^2 * J0(2 pi|xi|) d xi,")
print("et le noyau de Fourier J0 change de signe une infinité de fois. Toute borne de type")
print("Delsarte/LP exige un noyau POSITIF ; il faut donc retoucher le noyau à la main")
print("(c'est exactement le travail de Falconer 1981). Voilà la vraie raison de l'échec spectral.")
