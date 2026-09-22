"""
WHITELIST - Domaines mondialement connus et fiables.

Sert de garde-fou en amont du modèle ML : si l'URL analysée appartient
à un domaine de cette liste (ou à un sous-domaine direct), on considère
l'URL comme légitime sans même interroger le modèle. Cela évite les faux
positifs sur les cas les plus évidents (google.com, github.com, etc.)
et donne un filet de sécurité robuste, indépendant des biais possibles
du dataset d'entraînement.

Cette whitelist est volontairement courte et composée uniquement de
domaines mondialement reconnus (GAFAM, grands services techniques).
Elle ne remplace pas le modèle : toute URL absente de cette liste
passe par extract_features() + le modèle comme d'habitude.
"""

import re
from urllib.parse import urlparse

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
    """Retourne le hostname sans protocole ni www, en minuscules."""
    try:
        u = str(url).strip().lower()
        u = re.sub(r'^https?://', '', u)
        u = re.sub(r'^www\.', '', u)
        parsed = urlparse('http://' + u)
        return parsed.netloc or parsed.path.split('/')[0]
    except Exception:
        return ""


def est_domaine_fiable(url):
    """
    Vrai si l'URL appartient à un domaine de la whitelist
    (domaine exact ou sous-domaine direct, ex: docs.google.com).
    Attention : ne vérifie QUE le domaine, pas le chemin. Une URL
    de phishing hébergée en tant que sous-répertoire sur un service
    comme sites.google.com ne devrait normalement pas y être détectée
    (Google filtre ce type d'abus), mais cette whitelist reste un
    raccourci pragmatique, pas une garantie absolue de sécurité.
    """
    hostname = hostname_nu(url)
    if not hostname:
        return False
    for d in DOMAINES_FIABLES:
        if hostname == d or hostname.endswith("." + d):
            return True
    return False