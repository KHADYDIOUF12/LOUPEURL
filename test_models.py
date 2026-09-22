"""
DIAGNOSTIC : Vérification du modèle et des features
"""

import pandas as pd
import joblib
import numpy as np
from feature_extraction import extract_features, FEATURE_COLUMNS

print("=" * 60)
print("DIAGNOSTIC COMPLET")
print("=" * 60)

# 1. Charger le modèle et le scaler
try:
    model = joblib.load('modeles/best_model.pkl')
    scaler = joblib.load('modeles/scaler.pkl')
    print("✅ Modèle et scaler chargés")
except Exception as e:
    print(f"❌ Erreur de chargement : {e}")
    exit()

# 2. Tester une URL légitime
url_test = "https://www.amazon.fr"
features = extract_features(url_test)

if features is None:
    print("❌ Extraction échouée")
    exit()

print("\n📊 Features extraites :")
for key, value in features.items():
    print(f"  {key}: {value}")

# 3. Vérifier l'ordre des colonnes
df = pd.DataFrame([features])[FEATURE_COLUMNS]
print(f"\n📋 Ordre des colonnes : {list(df.columns)}")

# 4. Normaliser et prédire
X_scaled = scaler.transform(df)
proba = model.predict_proba(X_scaled)[0]
pred = model.predict(X_scaled)[0]

print(f"\n🎯 Résultat pour {url_test} :")
print(f"  Prédiction : {'MALVEILLANT' if pred == 1 else 'LEGITIME'}")
print(f"  Probabilité légitime : {proba[0]:.2%}")
print(f"  Probabilité malveillante : {proba[1]:.2%}")

# 5. Tester plusieurs URLs
print("\n" + "=" * 60)
print("TEST SUR PLUSIEURS URLS")
print("=" * 60)

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
        proba = model.predict_proba(X_scaled)[0]
        pred = model.predict(X_scaled)[0]
        verdict = "MALVEILLANT" if pred == 1 else "LEGITIME"
        print(f"\n{url}")
        print(f"  → {verdict} (malv: {proba[1]:.2%}, legit: {proba[0]:.2%})")