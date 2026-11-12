"""Completion de T8 sous deux conventions : ce qui reste + la carte delta*.
Le premier jet s'est enlise sur un reseau anisotrope a tres petit delta (matrices de
distances trop grosses) ; ici chaque cas est limite en duree et signale.
"""
import json, re, time, signal, random
import coloriage as K
import tangence

class Trop_long(Exception): pass
def _alarme(sig, frm): raise Trop_long()
signal.signal(signal.SIGALRM, _alarme)

RES = {"coloriage": [], "delta_etoile_strict": {}, "delta_etoile_large": {}, "ecarts": []}

# 1) recuperer les cas deja calcules dans le log du premier jet
lignes = open("t8_conventions.log").read().strip().split("\n")
for L in lignes:
    m = re.match(r"(\S+)\s+d=([\d.]+) omega (\d+)/(\d+) \| 6-coloriage large=(\w+) strict=(\w+)", L)
    if m:
        nom, d, ws, wl, ol, os_ = m.groups()
        RES["coloriage"].append(dict(reseau=nom, delta=float(d), omega_strict=int(ws),
                                     omega_large=int(wl), six_large=(ol == "True"),
                                     six_strict=(os_ == "True")))
print(f"recupere {len(RES['coloriage'])} cas du premier jet")

# 2) les deux reseaux restants, avec limite de duree
DEJA = {(r["reseau"], r["delta"]) for r in RES["coloriage"]}
for (rho, th, nom) in [(1.9, 70, "anisotrope"), (1.4, 100, "divers")]:
    for d in [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.98]:
        if (nom, d) in DEJA: continue
        try:
            signal.alarm(120)
            ws, wl = tangence.omega_deux(rho, th, d)
            ok_l, *_ = K.chercher(rho, th, d, mmax=24, verbose=False, convention="large")
            ok_s, *_ = K.chercher(rho, th, d, mmax=24, verbose=False, convention="strict")
            signal.alarm(0)
            RES["coloriage"].append(dict(reseau=nom, delta=d, omega_strict=ws, omega_large=wl,
                                         six_large=ok_l, six_strict=ok_s))
            print(f"  {nom} d={d}: omega {ws}/{wl} six {ok_l}/{ok_s}", flush=True)
        except Trop_long:
            signal.alarm(0)
            RES["coloriage"].append(dict(reseau=nom, delta=d, omega_strict=None, omega_large=None,
                                         six_large=None, six_strict=None, note="delai depasse"))
            print(f"  {nom} d={d}: DELAI DEPASSE (non conclu)", flush=True)

# 3) la carte : les conventions ne peuvent differer qu'en cas de tangence exacte.
#    On verifie que strict = large sur un echantillon, et on teste les rangees speciales.
pay = json.load(open("paysage.json"))
rnd = random.Random(4)
ech = 0; ec = 0
for _ in range(60):
    th = rnd.choice(pay["theta"]); rho = rnd.choice(pay["rho"]); d = rnd.choice(pay["delta"])
    ws, wl = tangence.omega_deux(rho, th, d)
    ech += 1
    if ws != wl:
        ec += 1; RES["ecarts"].append(dict(theta=th, rho=rho, delta=d, strict=ws, large=wl))
print(f"echantillon de {ech} points de la carte : {ec} ecarts entre conventions")
for th in (60, 90, 120):
    for rho in pay["rho"]:
        k = f"{th},{rho:.4f}"
        ds_s = ds_l = None
        for d in pay["delta"]:
            ws, wl = tangence.omega_deux(rho, th, d)
            if wl <= 6: ds_l = d
            if ws <= 6: ds_s = d
            if ws != wl: RES["ecarts"].append(dict(theta=th, rho=rho, delta=d, strict=ws, large=wl))
        RES["delta_etoile_strict"][k] = ds_s
        RES["delta_etoile_large"][k] = ds_l
    print(f"  rangee theta={th} faite", flush=True)
json.dump(RES, open("conventions.json", "w"), ensure_ascii=False)
print("ecrit conventions.json |",
      sum(1 for r in RES["coloriage"] if r.get("six_strict")),
      "6-coloriages (strict),",
      sum(1 for r in RES["coloriage"] if r.get("six_large")), "(large)")
