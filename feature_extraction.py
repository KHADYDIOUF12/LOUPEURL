"""
MODULE COMMUN : EXTRACTION DES FEATURES D'UNE URL
"""

import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    'login', 'signin', 'verify', 'secure', 'update', 'confirm',
    'account', 'bank', 'password', 'paypal', 'free', 'click',
    'win', 'prize', 'bonus', 'urgent', 'alert', 'support',
    'security', 'token', 'auth', 'verification', 'invoice', 'webscr'
]

FEATURE_COLUMNS = [
    'url_length', 'num_dots', 'num_slashes', 'num_digits',
    'num_special_chars', 'has_ip', 'num_subdomains', 'hostname_length',
    'path_length', 'num_params', 'suspicious_words',
    'num_hyphens', 'num_underscores', 'has_port', 'num_redirects',
    'tld_length'
]


def extract_features(url):
    if not isinstance(url, str) or len(url.strip()) == 0:
        return None

    try:
        url = url.strip().lower()

        # Retirer protocole + www
        url_nue = re.sub(r'^https?://', '', url)
        url_nue = re.sub(r'^www\.', '', url_nue)

        parsed = urlparse('http://' + url_nue)
        hostname = parsed.netloc or parsed.path.split('/')[0]
        path = parsed.path

        # ✅ SÉPARER LE PORT DU HOSTNAME
        hostname_sans_port = hostname.split(':')[0]

        word_count = sum(1 for w in SUSPICIOUS_WORDS if w in url_nue)
        num_subdomains = max(0, len(hostname_sans_port.split('.')) - 2)

        # ✅ DÉTECTION IP CORRIGÉE (sans le port)
        has_ip = 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname_sans_port) else 0
        has_port = 1 if ':' in hostname and hostname.split(':')[-1].isdigit() else 0

        features = {
            'url_length': len(url_nue),
            'num_dots': url_nue.count('.'),
            'num_slashes': url_nue.count('/'),
            'num_digits': sum(c.isdigit() for c in url_nue),
            'num_special_chars': len(re.findall(r'[@_\-!$&*=+?%#~|\[\]{}<>]', url_nue)),
            'has_ip': has_ip,
            'num_subdomains': num_subdomains,
            'hostname_length': len(hostname_sans_port),
            'path_length': len(path),
            'num_params': len(parsed.query.split('&')) if parsed.query else 0,
            'suspicious_words': word_count,
            'num_hyphens': url_nue.count('-'),
            'num_underscores': url_nue.count('_'),
            'has_port': has_port,
            'num_redirects': url_nue.count('//'),
            'tld_length': len(hostname_sans_port.split('.')[-1]) if '.' in hostname_sans_port else 0,
        }
        return features
    except Exception:
        return None