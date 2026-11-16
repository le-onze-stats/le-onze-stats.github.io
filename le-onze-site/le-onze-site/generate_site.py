import datetime, json, os

def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

D = json.load(open("data/data.json", encoding="utf-8"))
B = json.load(open("data/bios.json", encoding="utf-8"))
S = json.load(open("data/stats.json", encoding="utf-8"))
tpl = open("template.html", encoding="utf-8").read()

nb_clubs = sum(len(l["clubs"]) for l in D.values())
nb_joueurs = sum(len(c["effectif"]) for l in D.values() for c in l["clubs"])
if len(D) != 5 or nb_clubs < 90 or nb_joueurs < 2000:
    raise SystemExit(f"Données incomplètes ({nb_clubs} clubs, {nb_joueurs} joueurs) : arrêt par sécurité.")

mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
t = datetime.date.today()
date = f"{t.day} {mois[t.month - 1]} {t.year}"

out = (tpl.replace("__D__", js(D)).replace("__B__", js(B))
          .replace("__S__", js(S["joueurs"])).replace("__SFIN__", js(S["fin"]))
          .replace("__DATE__", date))
assert "__" not in out.split("<script>")[0] and "__D__" not in out
os.makedirs("public", exist_ok=True)
open("public/index.html", "w", encoding="utf-8").write(out)
print("Site généré :", len(out) // 1024, "Ko,", nb_clubs, "clubs,", nb_joueurs, "joueurs")
