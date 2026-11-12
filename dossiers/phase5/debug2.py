exec(open('treillis.py').read().split('# ----------families ----------')[0])
import itertools
cell=voronoi((1,0),(0,1)); print("cellule carré non normalisée:", [(round(x,3),round(y,3)) for x,y in cell], "diam",round(diam(cell),4))
k=(1-1e-3)/diam(cell); a=k; print("côté a =",round(a,5), "  1/√2 =",round(1/math.sqrt(2),5))
def shifted(i,j): 
    c=(i*a, j*a); return [(c[0]+k*x, c[1]+k*y) for x,y in cell]
for (i,j) in [(1,0),(2,0),(2,2),(1,1)]:
    lo=dmin(shifted(0,0),shifted(i,j)); hi=dmax(shifted(0,0),shifted(i,j))
    print(f"paire (0,0)-({i},{j}) : min={lo:.6f} max={hi:.6f} conflit={lo<1-1e-9 and hi>1+1e-9}")
