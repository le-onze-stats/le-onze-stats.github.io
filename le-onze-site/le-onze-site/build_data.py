import os, json, time, urllib.request, urllib.error

TOKEN = os.environ.get("FOOTBALL_TOKEN", "").strip()
if not TOKEN:
    raise SystemExit("La clé d'API n'est pas définie.")

LIGUES = {"FL1": "Ligue 1", "PD": "Liga", "PL": "Premier League",
          "BL1": "Bundesliga", "SA": "Série A"}

def appel(chemin):
    req = urllib.request.Request("https://api.football-data.org/v4" + chemin,
                                 headers={"X-Auth-Token": TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erreur {e.code} sur {chemin}")
    time.sleep(7)  # limite gratuite : 10 requêtes par minute
    return data

resultat = {}
for code, nom in LIGUES.items():
    print("Récupération :", nom)
    cl = appel(f"/competitions/{code}/standings")
    eq = appel(f"/competitions/{code}/teams")
    resultat[code] = {
        "nom": nom,
        "saison": cl["season"]["startDate"][:4],
        "classement": [{
            "position": l["position"], "club": l["team"]["id"],
            "joues": l["playedGames"], "victoires": l["won"],
            "nuls": l["draw"], "defaites": l["lost"],
            "buts_pour": l["goalsFor"], "buts_contre": l["goalsAgainst"],
            "points": l["points"]} for l in cl["standings"][0]["table"]],
        "clubs": [{
            "id": t["id"], "nom": t["name"], "court": t.get("shortName"),
            "logo": t.get("crest"), "fondation": t.get("founded"),
            "stade": t.get("venue"), "couleurs": t.get("clubColors"),
            "entraineur": (t.get("coach") or {}).get("name"),
            "effectif": [{
                "nom": j.get("name"), "poste": j.get("position"),
                "naissance": j.get("dateOfBirth"),
                "nationalite": j.get("nationality")}
                for j in t.get("squad", [])]} for t in eq["teams"]],
    }

os.makedirs("data", exist_ok=True)
with open("data/data.json", "w", encoding="utf-8") as f:
    json.dump(resultat, f, ensure_ascii=False, indent=1)
print("Terminé : data/data.json créé.")
