import csv, gzip, json, os, urllib.request
from collections import defaultdict
from outils import norm, cle_joueur

BASE = "https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/"
UA = {"User-Agent": "LeOnze/1.0 (projet etudiant, stats football)"}
os.makedirs("tm", exist_ok=True)

def telecharge(nom):
    chemin = os.path.join("tm", nom)
    if not os.path.exists(chemin):
        print("Téléchargement de", nom, "…")
        req = urllib.request.Request(BASE + nom, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r, open(chemin, "wb") as f:
            while True:
                bloc = r.read(1 << 20)
                if not bloc:
                    break
                f.write(bloc)
    return chemin

def lire(nom):
    with gzip.open(telecharge(nom), "rt", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)

def entier(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return 0

def nombre(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None

clubs = {r["club_id"]: r["name"] for r in lire("clubs.csv.gz")}
par_dob = defaultdict(list)
for r in lire("players.csv.gz"):
    if r.get("date_of_birth"):
        par_dob[r["date_of_birth"][:10]].append(r)

agg = defaultdict(dict)
derniere = ""
print("Lecture des matchs…")
for r in lire("appearances.csv.gz"):
    d = r["date"]
    derniere = max(derniere, d)
    a = agg[r["player_id"]].setdefault(r["player_club_id"], [9999, 0, 0, 0, 0, 0, 0, 0])
    an = int(d[:4])
    a[0] = min(a[0], an); a[1] = max(a[1], an); a[2] += 1
    a[3] += entier(r["goals"]); a[4] += entier(r["assists"])
    a[5] += entier(r["yellow_cards"]); a[6] += entier(r["red_cards"])
    a[7] += entier(r["minutes_played"])

def trouve(nom, dob):
    cands = par_dob.get(dob, [])
    n = norm(nom)
    for c in cands:
        if norm(c["name"]) == n:
            return c
    tn = set(n.split())
    for c in cands:
        tc = set(norm(c["name"]).split())
        if tc and (tc <= tn or tn <= tc):
            return c
    if len(cands) == 1 and set(norm(cands[0]["name"]).split()) & tn:
        return cands[0]
    return None

data = json.load(open("data/data.json", encoding="utf-8"))
stats, total = {}, 0
for ligue in data.values():
    for c in ligue["clubs"]:
        for j in c["effectif"]:
            if not j.get("nom") or not j.get("naissance"):
                continue
            total += 1
            t = trouve(j["nom"], j["naissance"][:10])
            if not t:
                continue
            car = sorted(([clubs.get(cid, "Autre club")] + a
                          for cid, a in agg.get(t["player_id"], {}).items()),
                         key=lambda x: x[1])
            stats[cle_joueur(j["nom"], j["naissance"])] = {
                "v": nombre(t.get("market_value_in_eur")),
                "vm": nombre(t.get("highest_market_value_in_eur")),
                "h": nombre(t.get("height_in_cm")),
                "pied": t.get("foot") or None,
                "ne": t.get("city_of_birth") or None,
                "fin": (t.get("contract_expiration_date") or "")[:10] or None,
                "tm": t.get("url"),
                "car": car,
            }

if len(stats) < 0.5 * total:
    raise SystemExit("Trop peu de joueurs reconnus : arrêt par sécurité.")
json.dump({"fin": derniere, "joueurs": stats}, open("data/stats.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"Joueurs reconnus : {len(stats)} sur {total}. Dernier match : {derniere}")
