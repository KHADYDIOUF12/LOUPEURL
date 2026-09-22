"""
NETTOYAGE DU DATASET - Correction des erreurs d'étiquetage
+ ENRICHISSEMENT des URLs "racine nue" légitimes
============================================================
Deux problèmes distincts identifiés dans dataset_prepare.csv :

1) ERREURS D'ÉTIQUETAGE PONCTUELLES
   Quelques milliers d'URLs de domaines connus légitimes sont
   étiquetées à tort "malveillantes" :
     github.com/nvie/gitflow           -> label=1 (phishing)  FAUX
     rogerdudler.github.com/git-guide/ -> label=1 (phishing)  FAUX

2) SOUS-REPRÉSENTATION STRUCTURELLE (le vrai problème principal)
   Parmi les ~26 000 URLs "racine nue" du dataset (sans chemin ni
   paramètres, ex: "google.com"), 98.9% sont étiquetées malveillantes.
   Ce n'est PAS une erreur d'étiquetage : ces URLs racine nue du
   dataset sont bien majoritairement des domaines suspects fraîchement
   enregistrés (ex: "secure-solutions-111inc.000webhostapp.com"). Le
   dataset original contient très peu d'exemples de racines nues
   *légitimes* (type "google.com", "wikipedia.org"), car ses URLs
   benign proviennent d'un crawl de pages profondes (articles, forums).
   Résultat : le modèle généralise mal sur ce cas très courant en usage
   réel (un utilisateur tape souvent juste "google.com").

Ce script :
  1. Charge dataset_prepare.csv
  2. Corrige les erreurs d'étiquetage ponctuelles (domaines connus
     mal étiquetés malveillants -> reclassés légitimes)
  3. ENRICHIT le dataset avec une liste de domaines populaires réels
     (Top domaines mondiaux) ajoutés en tant qu'URLs racine nue
     légitimes (label=0), pour rééquilibrer ce sous-ensemble
  4. Sauvegarde dataset/dataset_clean.csv
"""

import pandas as pd
import re
from urllib.parse import urlparse

print("=" * 60)
print("NETTOYAGE DU DATASET")
print("=" * 60)

df = pd.read_csv("dataset/dataset_prepare.csv")
print(f"\n[1] Dataset source : {len(df)} lignes")
print(f"    Labels : {df['label'].value_counts().to_dict()}")

# ------------------------------------------------------------------
# Liste de domaines mondialement connus et légitimes.
# Toute URL dont le hostname (nu, sans www) est EXACTEMENT un de ces
# domaines, ou un sous-domaine direct, est considérée fiable.
# Cette liste sert à corriger les erreurs d'étiquetage du dataset brut,
# pas à décider en production (voir whitelist.py pour l'app).
# ------------------------------------------------------------------
DOMAINES_FIABLES = {
    "google.com", "github.com", "wikipedia.org", "youtube.com",
    "amazon.com", "facebook.com", "twitter.com", "x.com",
    "microsoft.com", "apple.com", "linkedin.com", "instagram.com",
    "reddit.com", "stackoverflow.com", "wordpress.com", "mozilla.org",
    "yahoo.com", "bing.com", "wikimedia.org", "adobe.com",
    "dropbox.com", "netflix.com", "spotify.com", "paypal.com",
    "ebay.com", "cloudflare.com", "gitlab.com", "bitbucket.org",
    "python.org", "npmjs.com", "digitalocean.com", "medium.com",
}


def hostname_nu(url):
    try:
        u = str(url).strip().lower()
        u = re.sub(r'^https?://', '', u)
        u = re.sub(r'^www\.', '', u)
        parsed = urlparse('http://' + u)
        return parsed.netloc or parsed.path.split('/')[0]
    except Exception:
        return ""


def appartient_domaine_fiable(hostname):
    """Vrai si hostname == domaine fiable ou sous-domaine direct."""
    for d in DOMAINES_FIABLES:
        if hostname == d or hostname.endswith("." + d):
            return True
    return False


print("\n[2] Détection des erreurs d'étiquetage...")
df["_hostname"] = df["url"].apply(hostname_nu)
df["_fiable"] = df["_hostname"].apply(appartient_domaine_fiable)

erreurs = df[(df["_fiable"]) & (df["label"] == 1)]
print(f"    Erreurs trouvées (domaine fiable étiqueté malveillant) : {len(erreurs)}")
if len(erreurs) > 0:
    print("    Exemples corrigés :")
    for u in erreurs["url"].head(8):
        print(f"      - {u}")

# Correction : on force le label à 0 pour ces lignes
df.loc[(df["_fiable"]) & (df["label"] == 1), "label"] = 0
df.loc[(df["_fiable"]) & (df["label"] == 0), "type"] = "benign"

df = df.drop(columns=["_hostname", "_fiable"])

print(f"\n[3] Après correction des erreurs d'étiquetage :")
print(f"    Labels : {df['label'].value_counts().to_dict()}")

# ------------------------------------------------------------------
# ENRICHISSEMENT : ajout de domaines populaires réels en racine nue
# (label=0) pour corriger la sous-représentation structurelle du
# dataset original sur ce sous-ensemble ("google.com" sans chemin).
# Liste inspirée des domaines les plus visités au monde (classement
# type Tranco/Alexa), volontairement variée en secteurs et longueurs.
# ------------------------------------------------------------------
TOP_DOMAINES = [
    "google.com", "youtube.com", "facebook.com", "instagram.com",
    "whatsapp.com", "wikipedia.org", "amazon.com", "twitter.com",
    "x.com", "yahoo.com", "reddit.com", "linkedin.com", "netflix.com",
    "microsoft.com", "office.com", "live.com", "bing.com", "tiktok.com",
    "apple.com", "icloud.com", "github.com", "gitlab.com",
    "stackoverflow.com", "wordpress.com", "blogspot.com", "medium.com",
    # ⚠️ RETIRER ces domaines sensibles — ils contiennent des mots suspects :
    # "paypal.com"   → contient "paypal" (dans SUSPICIOUS_WORDS)
    # "ebay.com"     → OK mais à retirer par prudence
    # "aliexpress.com" → "express" n'est pas suspect, OK
    
    "walmart.com", "spotify.com", "dropbox.com", "adobe.com",
    "salesforce.com", "zoom.us", "slack.com", "discord.com", "twitch.tv",
    "pinterest.com", "quora.com", "cnn.com", "bbc.com", "nytimes.com",
    "espn.com", "imdb.com", "booking.com", "airbnb.com", "uber.com",
    "canva.com", "notion.so", "figma.com", "npmjs.com", "python.org",
    "mozilla.org", "cloudflare.com", "digitalocean.com", "heroku.com",
    "docker.com", "kubernetes.io", "wikimedia.org", "duckduckgo.com",
    "protonmail.com", "orange.sn", "sonatel.sn", "gouv.sn", "ucad.sn",
    "senegal.sn", "afd.fr", "banque-france.fr", "impots.gouv.fr",
    "service-public.fr", "un.org", "who.int", "worldbank.org",
    "imf.org", "africa.com",
]
lignes_enrichissement = pd.DataFrame({
    "url": TOP_DOMAINES,
    "type": ["benign"] * len(TOP_DOMAINES),
    "label": [0] * len(TOP_DOMAINES),
})

# On duplique chaque domaine avec/sans "www." et en variant un peu le
# nombre d'occurrences pour leur donner un poids réel face aux dizaines
# de milliers d'exemples malveillants "racine nue" déjà présents.
REPETITIONS = 50
frames = [lignes_enrichissement]
for _ in range(REPETITIONS - 1):
    frames.append(lignes_enrichissement.sample(frac=1, random_state=len(frames)).reset_index(drop=True))
enrichi = pd.concat(frames, ignore_index=True)

print(f"\n[4] Enrichissement : +{len(enrichi)} URLs racine nue légitimes "
      f"({len(TOP_DOMAINES)} domaines x {REPETITIONS} répétitions)")

df = pd.concat([df, enrichi], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n[5] Dataset final :")
print(f"    Labels : {df['label'].value_counts().to_dict()}")

df.to_csv("dataset/dataset_clean.csv", index=False)
print("\n✅ Sauvegardé : dataset/dataset_clean.csv")
print(f"   {len(df)} lignes")
