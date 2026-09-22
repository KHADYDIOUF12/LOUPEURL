"""
PHASE 2 : ÉQUILIBRAGE DU DATASET
Sous-échantillonnage de la classe majoritaire pour obtenir 50% / 50%
"""

import pandas as pd

print("=" * 60)
print("PHASE 2 : ÉQUILIBRAGE DES CLASSES")
print("=" * 60)

df = pd.read_csv('dataset/dataset_clean.csv')
print(f"\nShape avant équilibrage : {df.shape}")

legitimes = df[df['label'] == 0]
malveillants = df[df['label'] == 1]
print(f"   Légitimes   : {len(legitimes)}")
print(f"   Malveillants: {len(malveillants)}")

# Sous-échantillonnage : on ramène la classe majoritaire au niveau de la minoritaire
n_cible = min(len(legitimes), len(malveillants))
legitimes_eq = legitimes.sample(n=n_cible, random_state=42)
malveillants_eq = malveillants.sample(n=n_cible, random_state=42)

df_eq = pd.concat([legitimes_eq, malveillants_eq], ignore_index=True)

# Mélange aléatoire
df_eq = df_eq.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nShape après équilibrage : {df_eq.shape}")
print(f"   Répartition : {df_eq['label'].value_counts().to_dict()}")

df_eq.to_csv('dataset/dataset_balanced.csv', index=False)
print("\n   ✅ Sauvegardé : dataset/dataset_balanced.csv")