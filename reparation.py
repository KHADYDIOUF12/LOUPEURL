"""
REPARATION COMPLETE
1. Charge les features existantes
2. Entraîne un Random Forest propre (données scalées)
3. Évalue sa vraie performance
4. Sauvegarde best_model.pkl + scaler.pkl
5. Teste 3 URLs et affiche le verdict
"""

import pandas as pd
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from feature_extraction import extract_features, FEATURE_COLUMNS

print("=" * 60)
print("REPARATION COMPLETE")
print("=" * 60)

# 1. Chargement
data = pd.read_csv('features/features_dataset.csv')
print(f"1. Features : {data.shape[0]} lignes x {data.shape[1]} colonnes")
print(f"   Labels : {data['label'].value_counts().to_dict()}")

if len(data) < 100000:
    print("   ATTENTION : fichier features INCOMPLET (mode test 5000)")
    print("   -> Il faut relancer extraction_features.py en mode complet")

# 2. Split + normalisation
X = data.drop('label', axis=1)
y = data['label']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# 3. Entraînement
print("\n2. Entraînement Random Forest (données scalées)...")
rf = RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
rf.fit(X_train_s, y_train)

# 4. Évaluation
y_pred = rf.predict(X_test_s)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
print(f"   Accuracy : {acc:.4f} | F1 : {f1:.4f}")
if acc > 0.9:
    print("   -> DONNEES SAINES : le modèle est excellent")
else:
    print("   -> DONNEES CORROMPUES : il faut regénérer les features")

# 5. Sauvegarde
joblib.dump(rf, 'modeles/best_model.pkl')
joblib.dump(scaler, 'modeles/scaler.pkl')
print("\n3. Nouveaux modèles sauvegardés : best_model.pkl + scaler.pkl")

# 6. Test sur 3 URLs
print("\n4. TEST SUR 3 URLS")
urls = [
    ("MALV-1", "http://login-verify-bankofamerica.com/secure/update-account"),
    ("MALV-2", "http://192.168.1.105/paypal/login"),
    ("LEGIT-1", "https://www.google.com"),
]
for nom, url in urls:
    feats = extract_features(url)
    df = pd.DataFrame([feats])[FEATURE_COLUMNS]
    scaled = scaler.transform(df)
    proba = rf.predict_proba(scaled)[0]
    pred = rf.predict(scaled)[0]
    verdict = "MALVEILLANTE" if pred == 1 else "LEGITIME"
    print(f"{nom} -> {verdict} | P(malv)={proba[1]:.2%} | P(legit)={proba[0]:.2%}")

print("\n" + "=" * 60)
print("FIN - copie-moi tout ce qui s'affiche")
print("=" * 60)