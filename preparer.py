"""
PHASE 1 : PRÉPARATION DU DATASET
- Chargement du dataset Kaggle (+ enrichissement PhishTank si présent)
- Nettoyage : doublons, URLs vides, format
- Création de la colonne label (0 = légitime, 1 = malveillant)
"""

import pandas as pd
import os

print("=" * 60)
print("PHASE 1 : PRÉPARATION DU DATASET")
print("=" * 60)

# 1.1 Chargement
print("\n1.1 Chargement du dataset Kaggle...")
df = pd.read_csv('dataset/malicious_phish.csv')
print(f"   Shape initial : {df.shape}")
print(f"   Répartition : {df['type'].value_counts().to_dict()}")

# 1.2 Enrichissement PhishTank (si le fichier existe)
fichier_pt = 'dataset/phishtank_phishing.csv'
if os.path.exists(fichier_pt):
    print("\n1.2 Enrichissement avec PhishTank...")
    df_pt = pd.read_csv(fichier_pt)
    # Échantillon pour ne pas déséquilibrer (ex: 50 000)
    echantillon = df_pt.sample(n=min(50000, len(df_pt)), random_state=42)
    df = pd.concat([df, echantillon], ignore_index=True)
    print(f"   ✅ +{len(echantillon)} URLs PhishTank ajoutées")
else:
    print("\n1.2 Fichier PhishTank absent → on continue sans enrichissement.")

# 1.3 Nettoyage
print("\n1.3 Nettoyage...")

# Doublons
avant = len(df)
df = df.drop_duplicates(subset='url')
print(f"   Doublons supprimés : {avant - len(df)}")

# URLs vides ou invalides
df = df[df['url'].notna() & (df['url'].str.strip() != '')]
df['url'] = df['url'].str.strip()

# Normalisation du type (minuscules)
df['type'] = df['type'].str.lower().str.strip()

# Garder uniquement les 4 classes connues
classes_valides = ['benign', 'defacement', 'phishing', 'malware']
df = df[df['type'].isin(classes_valides)]
print(f"   Shape après nettoyage : {df.shape}")

# 1.4 Création du label binaire
# 0 = légitime (benign), 1 = malveillant (tout le reste)
df['label'] = (df['type'] != 'benign').astype(int)

print("\n1.4 Répartition finale :")
print(f"   {df['label'].value_counts().to_dict()}  (0 = légitime, 1 = malveillant)")

# 1.5 Sauvegarde
df.to_csv('dataset/dataset_prepare.csv', index=False)
print("\n   ✅ Sauvegardé : dataset/dataset_prepare.csv")