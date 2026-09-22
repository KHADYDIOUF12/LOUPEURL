"""
PHASE 0 : TÉLÉCHARGEMENT DES DONNÉES
- Kaggle   : Malicious URLs Dataset (651 191 URLs)
- PhishTank: URLs de phishing vérifiées (enrichissement + test)
"""

import os
import pandas as pd

os.makedirs('dataset', exist_ok=True)

# ------------------------------------------------------------
# 0.1 Kaggle : dataset principal
# ------------------------------------------------------------
print("=" * 60)
print("0.1 Téléchargement depuis Kaggle...")
print("=" * 60)

kaggle_ok = False
try:
    import kagglehub
    chemin = kagglehub.dataset_download("sid321axn/malicious-urls-dataset")
    print(f"   Dataset téléchargé dans : {chemin}")

    src = os.path.join(chemin, "malicious_phish.csv")
    if os.path.exists(src):
        dst = "dataset/malicious_phish.csv"
        os.replace(src, dst) if os.path.dirname(src) != "dataset" else None
        print(f"   ✅ Fichier copié : {dst}")
        kaggle_ok = True
except Exception as e:
    print(f"   ⚠️ Erreur kagglehub : {e}")

if not kaggle_ok:
    print("""
   ➡️ Télécharge manuellement le dataset :
      https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
      Puis place malicious_phish.csv dans le dossier dataset/
    """)

# ------------------------------------------------------------
# 0.2 PhishTank : URLs de phishing vérifiées (enrichissement)
# ------------------------------------------------------------
print("\n" + "=" * 60)
print("0.2 Téléchargement depuis PhishTank...")
print("=" * 60)

# Sans clé API : quelques téléchargements/jour max.
# Avec clé (gratuite, sur phishtank.com -> API) :
#   URL_DUMP = "https://data.phishtank.com/data/VOTRE_CLE/online-valid.csv"
URL_DUMP = "https://data.phishtank.com/data/online-valid.csv"

try:
    df_pt = pd.read_csv(URL_DUMP)
    print(f"   URLs brutes récupérées : {len(df_pt)}")

    # Garder uniquement les entrées vérifiées comme phishing
    if 'verified' in df_pt.columns:
        df_pt = df_pt[df_pt['verified'] == 'yes']
    if 'online' in df_pt.columns:
        df_pt = df_pt[df_pt['online'] == 'yes']

    # Conserver le même format que Kaggle : colonnes url + type
    df_pt = df_pt[['url']].copy()
    df_pt['type'] = 'phishing'
    df_pt = df_pt.drop_duplicates(subset='url')

    df_pt.to_csv("dataset/phishtank_phishing.csv", index=False)
    print(f"   ✅ URLs vérifiées enregistrées : {len(df_pt)}")
    print(f"   Fichier : dataset/phishtank_phishing.csv")
except Exception as e:
    print(f"   ⚠️ Erreur PhishTank (réseau ?) : {e}")
    print("   → Tu peux continuer avec le seul dataset Kaggle, l'enrichissement est optionnel.")

print("\n✅ Phase 0 terminée.")