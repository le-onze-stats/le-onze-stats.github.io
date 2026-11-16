import json, os, time, urllib.error, urllib.parse, urllib.request
from outils import norm, cle_joueur

API = "https://fr.wikipedia.org/w/api.php"
UA = {"User-Agent": "LeOnze/1.0 (projet etudiant, stats football)"}
MAX = 300  # nouveaux joueurs traités par exécution

def cherche(requete):
    params = {"action": "query", "generator": "search", "gsrsearch": requete,
              "gsrlimit": 4, "prop": "extracts|description|info", "inprop": "url",
              "exintro": 1, "explaintext": 1, "exsentences": 3, "exlimit": 4,
              "format": "json", "formatversion": 2}
    url = API + "?" + urllib.parse.urlencode(params)
    for essai in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                pages = json.load(r).get("query", {}).get("pages", [])
            return sorted(pages, key=lambda p: p.get("index", 99))
        except Exception:
            time.sleep(10 * (essai + 1))
    raise RuntimeError("Wikipédia ne répond pas")

def couper(txt, n=600):
    txt = (txt or "").strip()
    if len(txt) <= n:
        return txt
    cut = txt[:n].rfind(". ")
    return txt[:cut + 1] if cut > 150 else txt[:n].rstrip() + "…"

def bio_joueur(nom):
    for p in cherche(nom + " footballeur"):
        if norm(p["title"].split(" (")[0]) == norm(nom) and "foot" in norm(p.get("description", "")):
            return {"txt": couper(p.get("extract")), "url": p["fullurl"]}
    return {}

data = json.load(open("data/data.json", encoding="utf-8"))
bios = json.load(open("data/bios.json", encoding="utf-8"))
nouveaux = []
for l in data.values():
    for c in l["clubs"]:
        for j in c["effectif"]:
            if j.get("nom") and j.get("naissance"):
                cle = cle_joueur(j["nom"], j["naissance"])
                if cle not in bios["joueurs"]:
                    nouveaux.append((cle, j["nom"]))

print(len(nouveaux), "nouveaux joueurs sans biographie")
try:
    for cle, nom in nouveaux[:MAX]:
        bios["joueurs"][cle] = bio_joueur(nom)
        time.sleep(0.3)
except RuntimeError as e:
    print("Arrêt anticipé :", e)
json.dump(bios, open("data/bios.json", "w", encoding="utf-8"), ensure_ascii=False)
print("Biographies enregistrées.")
