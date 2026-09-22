"""
CORRECTION D'URGENCE - Ré-entraînement avec vérification
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("CORRECTION D'URGENCE")
print("=" * 60)

# 1. Charger et examiner les données
data = pd.read_csv('features/features_dataset.csv')
print(f"\n📊 Dataset : {len(data)} lignes")
print(f"   Labels : {data['label'].value_counts().to_dict()}")

# 2. Vérifier l'équilibrage
if data['label'].value_counts()[0] == data['label'].value_counts()[1]:
    print("   ✅ Dataset équilibré")
else:
    print("   ⚠️ Dataset déséquilibré !")
    # Ré-équilibrer
    min_count = min(data['label'].value_counts())
    df_0 = data[data['label'] == 0].sample(n=min_count, random_state=42)
    df_1 = data[data['label'] == 1].sample(n=min_count, random_state=42)
    data = pd.concat([df_0, df_1]).sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"   ✅ Rééquilibré : {data['label'].value_counts().to_dict()}")

# 3. Séparer features et label
X = data.drop('label', axis=1)
y = data['label']

# 4. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Normalisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 6. Entraînement avec régularisation
print("\n🔹 Entraînement du modèle...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=20,
    min_samples_leaf=10,
    class_weight='balanced',  # Important !
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train_scaled, y_train)

# 7. Évaluation
y_pred = rf.predict(X_test_scaled)
print(f"\n📊 Performance :")
print(f"   Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"   F1-Score: {f1_score(y_test, y_pred):.4f}")

print(f"\n📋 Rapport de classification :")
print(classification_report(y_test, y_pred, target_names=['Légitime', 'Malveillant']))

print(f"\n📊 Matrice de confusion :")
cm = confusion_matrix(y_test, y_pred)
print(cm)
print(f"   Vrais positifs (malv): {cm[1][1]}")
print(f"   Faux positifs (malv): {cm[0][1]}")  # <-- Important !

# 8. Sauvegarder
joblib.dump(rf, 'modeles/best_model.pkl')
joblib.dump(scaler, 'modeles/scaler.pkl')
print("\n✅ Modèles sauvegardés")

# 9. Test
print("\n" + "=" * 60)
print("TEST FINAL")
print("=" * 60)

from feature_extraction import extract_features, FEATURE_COLUMNS

test_urls = [
    "https://www.google.com",
    "https://www.amazon.fr",
    "https://www.wikipedia.org",
    "http://login-verify-bankofamerica.com/secure/update-account",
    "http://paypal.com.security-verify.xyz:8080/signin"
]

for url in test_urls:
    features = extract_features(url)
    if features:
        df = pd.DataFrame([features])[FEATURE_COLUMNS]
        X_scaled = scaler.transform(df)
        proba = rf.predict_proba(X_scaled)[0]
        pred = rf.predict(X_scaled)[0]
        verdict = "MALVEILLANT" if pred == 1 else "LEGITIME"
        print(f"\n{url[:50]}...")
        print(f"  → {verdict} (malv: {proba[1]:.2%}, legit: {proba[0]:.2%})")