# LoupeURL — Installation

Deux services à lancer séparément.

## 1. API mail (Node.js)

```bash
cd loupeurl-mail-api
npm install
cp .env.example .env
```

Éditer `.env` :
- `MAIL_USER` : ta vraie adresse Gmail (ou autre fournisseur)
- `MAIL_PASS` : un **mot de passe d'application** (pas ton mot de passe normal)
  → À générer sur https://myaccount.google.com/apppasswords
  (nécessite la validation en 2 étapes activée sur le compte Google)
- `MAIL_FROM_NAME` : le nom affiché à l'expéditeur, ex. `LoupeURL Sécurité`

Puis lancer :
```bash
node server.js
```
Le serveur écoute sur `http://localhost:3001`.

## 2. Application Streamlit

```bash
cd loupeurl-app
pip install -r requirements.txt   # streamlit, pandas, joblib, scikit-learn, fpdf2, requests
streamlit run app.py
```

L'app cherche l'API mail sur `http://localhost:3001` (modifiable en haut de `app.py`,
variable `MAIL_API_URL`). Si l'API n'est pas démarrée, la page Sensibilisation
affiche un message d'erreur clair mais le reste de l'app (analyse d'URL) fonctionne
normalement — c'est un design volontairement découplé.

## Fonctionnement de l'identité d'expéditeur

Le "From" d'un email a deux parties :
- l'**adresse technique** : forcément une boîte que tu contrôles réellement,
  configurée dans `.env` (`MAIL_USER`). Impossible d'envoyer "depuis" une adresse
  qui n'est pas la tienne — ce serait détecté comme spoofing.
- le **nom affiché** : totalement libre, réglé dans `.env` (`MAIL_FROM_NAME`).
  C'est ce que voit le destinataire dans son client mail : "LoupeURL Sécurité"
  et non ton nom personnel, même si l'envoi technique transite par ta boîte.

## Ajouter un article de sensibilisation

Éditer `loupeurl-mail-api/articles.js` et ajouter une entrée au même format
(id, titre, resume, corpsHtml). Redémarrer le serveur Node — l'app Streamlit
récupère la liste dynamiquement via `/api/articles`, aucune modification
côté Python n'est nécessaire.
