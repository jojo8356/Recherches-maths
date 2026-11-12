"""Phase 7 - cellules a bords courbes : on remplace chaque arete partagee du pavage
par un arc de cercle de rayon R (R=1 = l'hypothese que le preprint de 2025 interdit)."""
import math, random, sys, itertools
import numpy as np
sys.path.insert(0,'.')
from partition2 import voronoi_tore, diam, wrap, normaliser, clique_max, k_color

# ---------- distance entre polygones, vectorisee ----------
def dmin_np(A,B):
    A=np.asarray(A); B=np.asarray(B)
    A2=A[:,None,:]; B1=B[None,:,:]; B2=np.roll(B,-1,axis=0)[None,:,:]
    AB=B2-B1
    L=(AB**2).sum(-1); L=np.where(L==0,1e-30,L)
    t=np.clip(((A2-B1)*AB).sum(-1)/L,0,1)
    proj=B1+t[...,None]*AB
    d1=np.sqrt(((A2-proj)**2).sum(-1)).min()
    B2_=B[:,None,:]; A1=A[None,:,:]; A2_=np.roll(A,-1,axis=0)[None,:,:]
    AB2=A2_-A1
    L2=(AB2**2).sum(-1); L2=np.where(L2==0,1e-30,L2)
    t2=np.clip(((B2_-A1)*AB2).sum(-1)/L2,0,1)
    proj2=A1+t2[...,None]*AB2
    d2=np.sqrt(((B2_-proj2)**2).sum(-1)).min()
    return min(d1,d2)
def dmax_np(A,B):
    A=np.asarray(A); B=np.asarray(B)
    return float(np.sqrt(((A[:,None,:]-B[None,:,:])**2).sum(-1)).max())

# ---------- arcs ----------
def arc_points(A,B,sag,M):
    """M+1 points de A a B, arc de fleche sag (>0 = vers la normale +90 de A->B)."""
    ax,ay=A; bx,by=B
    L=math.hypot(bx-ax,by-ay)
    if abs(sag)<1e-12: return [(ax+(bx-ax)*k/M, ay+(by-ay)*k/M) for k in range(M+1)]
    nx,ny=-(by-ay)/L,(bx-ax)/L
    out=[]
    for k in range(M+1):
        t=k/M; f=4*t*(1-t)          # 0 aux bouts, 1 au milieu
        out.append((ax+(bx-ax)*t+nx*sag*f, ay+(by-ay)*t+ny*sag*f))
    return out
def sag_from_R(L,R):
    """fleche d'un arc de rayon R sur une corde de longueur L (None si R < L/2)."""
    if R is None: return None
    if R<L/2: return None
    return R-math.sqrt(R*R-L*L/4)

# ---------- construction du pavage courbe ----------
def pavage_courbe(seeds,U1,U2,R,M=6,sign_seed=0,verbose=False):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return None
    n=len(cells)
    # index des aretes partagees : cle = paire de sommets arrondis
    def key(p): return (round(p[0],9),round(p[1],9))
    aretes={}   # frozenset({a,b}) -> (A,B canoniques, cellules)
    for i,c in enumerate(cells):
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            ka,kb=key(a),key(b)
            if ka==kb: continue
            e=frozenset((ka,kb))
            aretes.setdefault(e,{"A":min(ka,kb),"B":max(ka,kb),"cells":set()})["cells"].add(i)
    rnd=random.Random(sign_seed)
    signe={}
    for e,info in aretes.items():
        if len(info["cells"])==2: signe[e]=rnd.choice((1,-1))   # une cellule gagne, l'autre perd
        else: signe[e]=0
    # polygones courbes
    out=[]
    for i,c in enumerate(cells):
        poly=[]
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            ka,kb=key(a),key(b)
            if ka==kb: continue
            e=frozenset((ka,kb)); info=aretes[e]
            A,B=info["A"],info["B"]; L=math.dist(A,B)
            s=sag_from_R(L,R)
            if s is None or signe[e]==0: s_=0.0
            else: s_=s*signe[e]
            pts=arc_points(A,B,s_,M)
            # orienter de a vers b
            if math.dist(pts[0],a)>1e-9: pts=pts[::-1]
            poly.extend(pts[:-1] if k<len(c)-1 else pts)
        # nettoyage des doublons consecutifs
        clean=[poly[0]]
        for p in poly[1:]:
            if math.dist(p,clean[-1])>1e-12: clean.append(p)
        if math.dist(clean[0],clean[-1])<1e-12: clean.pop()
        out.append(clean)
    return out, aretes

def aire(poly):
    s=0
    for k in range(len(poly)):
        x1,y1=poly[k]; x2,y2=poly[(k+1)%len(poly)]
        s+=x1*y2-x2*y1
    return s/2

def graphe_np(cells,U1,U2,margin=0.0):
    n=len(cells)
    cen=[(sum(p[0] for p in c)/len(c),sum(p[1] for p in c)/len(c)) for c in cells]
    rad=[max(math.dist(q,cc) for q in c) for c,cc in zip(cells,cen)]
    adj=[set() for _ in range(n)]; mm=[]
    for i in range(n):
        for j in range(i+1,n):
            dv=wrap((cen[j][0]-cen[i][0],cen[j][1]-cen[i][1]),U1,U2)
            if math.hypot(*dv)>1.0+rad[i]+rad[j]+0.05: continue
            B=[(x-cen[j][0]+cen[i][0]+dv[0], y-cen[j][1]+cen[i][1]+dv[1]) for x,y in cells[j]]
            lo=dmin_np(cells[i],B); hi=dmax_np(cells[i],B)
            if lo<=1+margin and hi>=1-margin:
                adj[i].add(j); adj[j].add(i); mm.append(min(hi-1,1-lo))
    return adj,mm

# ---------- version corrigee : appariement des aretes modulo la periode ----------
def pavage_courbe2(seeds,U1,U2,R,M=6,sign_seed=0,verbose=False):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return None
    def key(p):
        q=wrap(p,U1,U2); return (round(q[0],6),round(q[1],6))
    aretes={}
    for i,c in enumerate(cells):
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            ka,kb=key(a),key(b)
            if ka==kb: continue
            e=frozenset((ka,kb))
            aretes.setdefault(e,{"A":min(ka,kb),"B":max(ka,kb),"cells":set()})["cells"].add(i)
    part=sum(1 for v in aretes.values() if len(v["cells"])==2)
    if verbose: print(f"    aretes : {len(aretes)} distinctes, {part} partagees par 2 cellules ({100*part/len(aretes):.0f}%)")
    rnd=random.Random(sign_seed); signe={}
    for e,info in aretes.items():
        signe[e]=rnd.choice((1,-1)) if len(info["cells"])==2 else 0
    out=[]
    for i,c in enumerate(cells):
        poly=[]
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            ka,kb=key(a),key(b)
            if ka==kb: continue
            e=frozenset((ka,kb)); info=aretes[e]
            A,B=info["A"],info["B"]; L=math.dist(A,B)
            sag=sag_from_R(L,R)
            if sag is None or signe[e]==0: s_=0.0
            else:
                dcan=((B[0]-A[0])/L,(B[1]-A[1])/L)
                Lab=math.dist(a,b); dact=((b[0]-a[0])/Lab,(b[1]-a[1])/Lab)
                s_=sag*signe[e]*(1 if dcan[0]*dact[0]+dcan[1]*dact[1]>0 else -1)
            pts=arc_points(a,b,s_,M)
            poly.extend(pts[:-1] if k<len(c)-1 else pts)
        clean=[poly[0]]
        for p in poly[1:]:
            if math.dist(p,clean[-1])>1e-12: clean.append(p)
        if math.dist(clean[0],clean[-1])<1e-12: clean.pop()
        out.append(clean)
    return out, aretes

# ---------- version 3 : signe determine par le milieu de l'arete (invariant par translation) ----------
def _signe_milieu(a,b,U1,U2):
    m=wrap(((a[0]+b[0])/2,(a[1]+b[1])/2),U1,U2)
    h=math.sin(m[0]*12.9898+m[1]*78.233)*43758.5453
    return 1.0 if (h-math.floor(h))>0.5 else -1.0
def pavage_courbe3(seeds,U1,U2,R,M=6,verbose=False):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return None
    out=[]
    for c in cells:
        poly=[]
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            L=math.dist(a,b)
            sag=sag_from_R(L,R) if R else None
            if sag is None: pts=arc_points(a,b,0.0,M)
            else: pts=arc_points(a,b,sag*_signe_milieu(a,b,U1,U2),M)
            poly.extend(pts[:-1] if k<len(c)-1 else pts)
        clean=[poly[0]]
        for p in poly[1:]:
            if math.dist(p,clean[-1])>1e-12: clean.append(p)
        if math.dist(clean[0],clean[-1])<1e-12: clean.pop()
        out.append(clean)
    return out

# ---------- version 4 : signe = fonction periodique CONTINUE du milieu ----------
def _coords_basis(v,U1,U2):
    det=U1[0]*U2[1]-U1[1]*U2[0]
    return ((v[0]*U2[1]-v[1]*U2[0])/det,(U1[0]*v[1]-U1[1]*v[0])/det)
def _signe_periodique(a,b,U1,U2):
    m=((a[0]+b[0])/2,(a[1]+b[1])/2)
    u,v=_coords_basis(m,U1,U2)
    g=math.sin(2*math.pi*u+1.7)+0.62*math.sin(2*math.pi*v+0.9)+0.41*math.sin(2*math.pi*(u+v)+2.3)
    return 1.0 if g>0 else -1.0
def pavage_courbe4(seeds,U1,U2,R,M=6):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return None
    out=[]
    for c in cells:
        poly=[]
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            L=math.dist(a,b); sag=sag_from_R(L,R) if R else None
            pts=arc_points(a,b,0.0 if sag is None else sag*_signe_periodique(a,b,U1,U2),M)
            poly.extend(pts[:-1] if k<len(c)-1 else pts)
        clean=[poly[0]]
        for p in poly[1:]:
            if math.dist(p,clean[-1])>1e-12: clean.append(p)
        if math.dist(clean[0],clean[-1])<1e-12: clean.pop()
        out.append(clean)
    return out

# ---------- version 5 : signe antisymetrique, invariant par translation ----------
def _f_per(p,U1,U2):
    u,v=_coords_basis(p,U1,U2)
    return (math.sin(2*math.pi*u+1.3)+0.7*math.sin(2*math.pi*v+2.1)
            +0.3*math.sin(2*math.pi*(u+v)+0.4)+0.17*math.sin(2*math.pi*(2*u-v)))
def _sigma(a,b,U1,U2):
    """+1 si a est canoniquement avant b ; antisymetrique par construction."""
    fa,fb=_f_per(a,U1,U2),_f_per(b,U1,U2)
    if abs(fa-fb)<1e-13: fa+=1e-9*(1 if a[0]<b[0] else -1)
    return 1.0 if fa<fb else -1.0
def pavage_courbe5(seeds,U1,U2,R,M=6):
    cells=voronoi_tore(seeds,U1,U2)
    if cells is None: return None
    out=[]
    for c in cells:
        poly=[]
        for k in range(len(c)):
            a=c[k]; b=c[(k+1)%len(c)]
            L=math.dist(a,b); sag=sag_from_R(L,R) if R else None
            s=0.0 if sag is None else sag*_sigma(a,b,U1,U2)
            pts=arc_points(a,b,s,M)
            poly.extend(pts[:-1] if k<len(c)-1 else pts)
        clean=[poly[0]]
        for p in poly[1:]:
            if math.dist(p,clean[-1])>1e-12: clean.append(p)
        if math.dist(clean[0],clean[-1])<1e-12: clean.pop()
        out.append(clean)
    return out
