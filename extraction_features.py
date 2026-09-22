import pandas as pd
import time

from feature_extraction import extract_features, FEATURE_COLUMNS

print("=" * 60)
print("PHASE 3 : EXTRACTION DES FEATURES")
print("=" * 60)

df = pd.read_csv("dataset/dataset_clean.csv")

print(f"\nURLs à traiter : {len(df)}")
print(f"Nombre de features : {len(FEATURE_COLUMNS)}")
print(f"Features : {FEATURE_COLUMNS}")

start = time.time()

features_list = []
labels_list = []

total = len(df)

for i, row in df.iterrows():

    url = row["url"]
    label = row["label"]

    features = extract_features(url)

    if features is not None:
        features_list.append(features)
        labels_list.append(label)

    if (i + 1) % 50000 == 0:
        print(f"    {i + 1}/{total} URLs traitées...")

elapsed = time.time() - start

df_features = pd.DataFrame(
    features_list,
    columns=FEATURE_COLUMNS
)

df_features["label"] = labels_list

print("\n" + "=" * 60)
print("RÉSULTAT")
print("=" * 60)

print(f"Shape : {df_features.shape}")
print(f"Nombre de features : {len(FEATURE_COLUMNS)}")
print(f"Répartition : {df_features['label'].value_counts().to_dict()}")

df_features.to_csv(
    "features/features_dataset.csv",
    index=False
)

print("\n✅ Sauvegardé : features/features_dataset.csv")
print(f"⏱ Temps : {elapsed:.2f}s")