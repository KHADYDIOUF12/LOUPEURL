"""
ENTRAINEMENT : utilise features_dataset.csv (déjà extrait)
"""

import pandas as pd
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

print("=" * 60)
print("ENTRAINEMENT DU MODELE")
print("=" * 60)

# ==================================================================
# 1. CHARGER LES FEATURES DÉJÀ EXTRAITES
# ==================================================================
df = pd.read_csv('features/features_dataset.csv')
print(f"\n[1] Features chargées : {df.shape}")
print(f"    Répartition AVANT équilibrage : {df['label'].value_counts().to_dict()}")

# ==================================================================
# 2. ÉQUILIBRAGE 50/50
# ==================================================================
legitimes = df[df['label'] == 0]
malveillants = df[df['label'] == 1]
n_cible = min(len(legitimes), len(malveillants))
print(f"\n[2] Équilibrage à {n_cible} par classe...")

df_eq = pd.concat([
    legitimes.sample(n=n_cible, random_state=42),
    malveillants.sample(n=n_cible, random_state=42),
], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"    Répartition APRÈS équilibrage : {df_eq['label'].value_counts().to_dict()}")
print(f"    Total : {len(df_eq)} lignes")

# ==================================================================
# 3. SPLIT
# ==================================================================
FEATURE_COLUMNS = [
    'url_length', 'num_dots', 'num_slashes', 'num_digits',
    'num_special_chars', 'has_ip', 'num_subdomains', 'hostname_length',
    'path_length', 'num_params', 'suspicious_words',
    'num_hyphens', 'num_underscores', 'has_port', 'num_redirects',
    'tld_length'
]

X = df_eq[FEATURE_COLUMNS]
y = df_eq['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(f"\n[3] Split : {len(X_train)} train / {len(X_test)} test")

# ==================================================================
# 4. NORMALISATION
# ==================================================================
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ==================================================================
# 5. ENTRAINEMENT
# ==================================================================
print("\n[4] Entraînement Random Forest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=25,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',   # ✅ CRUCIAL : compense tout déséquilibre résiduel
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train_s, y_train)

# ==================================================================
# 6. ÉVALUATION
# ==================================================================
y_pred = rf.predict(X_test_s)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
print(f"\n[5] Résultats :")
print(f"    Accuracy : {acc:.4f}")
print(f"    F1-Score : {f1:.4f}")
print()
print(classification_report(y_test, y_pred, target_names=['Légitime', 'Malveillant']))

# ==================================================================
# 7. IMPORTANCE DES FEATURES
# ==================================================================
print("[6] Importance des features :")
importances = sorted(zip(FEATURE_COLUMNS, rf.feature_importances_), key=lambda x: -x[1])
for nom, imp in importances:
    print(f"    {nom:20s} : {imp:.4f}")

# ==================================================================
# 8. SAUVEGARDE
# ==================================================================
joblib.dump(rf, 'modeles/best_model.pkl')
joblib.dump(scaler, 'modeles/scaler.pkl')
print("\n[7] Modeles sauvegardes : best_model.pkl + scaler.pkl")

# ==================================================================
# 9. TEST FINAL SUR URLs RÉELLES
# ==================================================================
print("\n[8] VERDICT FINAL :")
from feature_extraction import extract_features
from whitelist import est_domaine_fiable

tests = [
    ("LEGITIME",   "https://www.google.com"),
    ("LEGITIME",   "https://www.wikipedia.org"),
    ("LEGITIME",   "https://www.github.com"),
    ("LEGITIME",   "https://www.amazon.fr"),
    ("PHISHING",   "http://login-verify-bankofamerica.com/secure/update-account"),
    ("IP SUSPECTE","http://192.168.1.105/paypal/login"),
    ("PHISHING",   "http://paypal.com.security-verify.xyz:8080/signin"),
    ("PHISHING",   "http://192.168.1.1:8080/~admin/paypal/verify/update/account/login.php?cmd=steal"),
]

for attente, url in tests:
    # Whitelist
    if est_domaine_fiable(url):
        print(f"  ✅ {attente:11s} -> LEGITIME (whitelist) | {url}")
        continue
    
    f = extract_features(url)
    if f is None:
        print(f"  ❌ {attente:11s} -> Extraction échouée   | {url}")
        continue
    
    s = scaler.transform(pd.DataFrame([f])[FEATURE_COLUMNS])
    p = rf.predict_proba(s)[0]
    verdict = "MALVEILLANTE" if p[1] >= 0.5 else "LEGITIME"
    attendu = "MALVEILLANTE" if attente in ("PHISHING", "IP SUSPECTE") else "LEGITIME"
    ok = "OK " if verdict == attendu else "KO "
    print(f"  {ok} {attente:11s} -> {verdict:12s} | P(malv)={p[1]:.2%} | {url}")