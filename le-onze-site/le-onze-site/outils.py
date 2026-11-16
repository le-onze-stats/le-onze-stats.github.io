import re, unicodedata

def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def cle_joueur(nom, naissance):
    """Clé stable d'un joueur : nom sans accents + date de naissance."""
    return re.sub(r"[^a-z0-9]+", "-", norm(nom)).strip("-") + "-" + (naissance or "")[:10]
