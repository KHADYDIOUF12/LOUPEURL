/**
 * ARTICLES DE SENSIBILISATION - LoupeURL
 * Chaque article a un id, un titre, une accroche courte (résumé affiché
 * dans l'interface Streamlit) et un corps HTML complet (envoyé par email).
 */

const ARTICLES = {
  phishing: {
    id: "phishing",
    titre: "Le phishing : comprendre et éviter le piège",
    resume: "Comment les cybercriminels imitent des sites de confiance pour voler vos identifiants.",
    corpsHtml: `
      <h2>Qu'est-ce que le phishing ?</h2>
      <p>Le phishing (hameçonnage) est une technique par laquelle un cybercriminel se fait
      passer pour une entité de confiance (banque, réseau social, service en ligne) afin de
      vous inciter à révéler des informations confidentielles : identifiants, mots de passe,
      numéros de carte bancaire.</p>
      <h3>Comment le reconnaître ?</h3>
      <ul>
        <li>Une adresse web qui ressemble au site légitime mais avec une variation subtile
        (ex : "go0gle.com" au lieu de "google.com")</li>
        <li>Un message créant un sentiment d'urgence ("votre compte sera suspendu dans 24h")</li>
        <li>Des fautes d'orthographe ou une mise en forme approximative</li>
        <li>Une demande d'informations sensibles par email ou SMS</li>
      </ul>
      <h3>Comment se protéger ?</h3>
      <ul>
        <li>Ne cliquez jamais directement sur un lien reçu par email pour vous connecter à un
        service sensible — tapez l'adresse vous-même dans le navigateur</li>
        <li>Vérifiez l'adresse exacte de l'expéditeur, pas seulement le nom affiché</li>
        <li>Activez la double authentification (2FA) partout où c'est possible</li>
        <li>En cas de doute, contactez directement l'organisme par un canal connu</li>
      </ul>
    `,
  },

  ransomware: {
    id: "ransomware",
    titre: "Ransomware : quand vos données sont prises en otage",
    resume: "Un logiciel malveillant qui chiffre vos fichiers et exige une rançon pour les débloquer.",
    corpsHtml: `
      <h2>Qu'est-ce qu'un ransomware ?</h2>
      <p>Un ransomware (rançongiciel) est un logiciel malveillant qui chiffre les fichiers
      d'un ordinateur ou d'un réseau, les rendant inaccessibles, puis exige le paiement d'une
      rançon (souvent en cryptomonnaie) en échange de la clé de déchiffrement.</p>
      <h3>Comment l'infection se produit-elle ?</h3>
      <ul>
        <li>Ouverture d'une pièce jointe piégée reçue par email</li>
        <li>Clic sur une URL malveillante menant à un téléchargement automatique</li>
        <li>Exploitation d'une faille de sécurité non corrigée (mise à jour manquante)</li>
        <li>Connexion à distance mal sécurisée (RDP exposé sur Internet)</li>
      </ul>
      <h3>Comment se protéger ?</h3>
      <ul>
        <li>Effectuez des sauvegardes régulières, déconnectées du réseau principal</li>
        <li>Maintenez vos systèmes et logiciels à jour</li>
        <li>Ne jamais ouvrir de pièce jointe ou de lien d'un expéditeur inconnu ou suspect</li>
        <li>Ne payez jamais la rançon : rien ne garantit la récupération des données, et cela
        finance les cybercriminels</li>
      </ul>
    `,
  },

  url_malveillante: {
    id: "url_malveillante",
    titre: "URL malveillantes : la porte d'entrée des cyberattaques",
    resume: "Comment une simple adresse web peut compromettre votre sécurité en un clic.",
    corpsHtml: `
      <h2>Qu'est-ce qu'une URL malveillante ?</h2>
      <p>Une URL malveillante est une adresse web conçue pour nuire à l'utilisateur : voler
      des informations, installer un logiciel malveillant, ou rediriger vers un site
      frauduleux. Elle constitue la porte d'entrée de la majorité des cyberattaques actuelles.</p>
      <h3>Les signaux d'alerte</h3>
      <ul>
        <li>Une adresse IP à la place d'un nom de domaine (ex : http://192.168.1.1/login)</li>
        <li>De nombreux sous-domaines empilés pour masquer le vrai domaine</li>
        <li>Des mots-clés comme "verify", "secure", "account" combinés à un domaine inconnu</li>
        <li>Une URL anormalement longue avec des paramètres incompréhensibles</li>
      </ul>
      <h3>Bonnes pratiques</h3>
      <ul>
        <li>Survolez toujours un lien avant de cliquer pour voir la vraie destination</li>
        <li>Utilisez un outil de vérification d'URL comme LoupeURL avant d'accéder à un site
        douteux</li>
        <li>Méfiez-vous des URL raccourcies (bit.ly, tinyurl) dont la destination est cachée</li>
      </ul>
    `,
  },

  ingenierie_sociale: {
    id: "ingenierie_sociale",
    titre: "L'ingénierie sociale : manipuler l'humain plutôt que la machine",
    resume: "La faille de sécurité la plus exploitée n'est pas technique, elle est humaine.",
    corpsHtml: `
      <h2>Qu'est-ce que l'ingénierie sociale ?</h2>
      <p>L'ingénierie sociale regroupe les techniques de manipulation psychologique visant à
      pousser une personne à divulguer des informations confidentielles ou à effectuer une
      action compromettante, sans passer par une faille technique.</p>
      <h3>Techniques courantes</h3>
      <ul>
        <li>Le prétexte : se faire passer pour un collègue, un technicien ou un supérieur</li>
        <li>L'urgence artificielle : créer une pression temporelle pour empêcher la réflexion</li>
        <li>L'appât : proposer un cadeau ou une offre trop belle pour être vraie</li>
      </ul>
      <h3>Comment s'en prémunir ?</h3>
      <ul>
        <li>Toujours vérifier l'identité d'un interlocuteur par un canal indépendant avant
        toute action sensible</li>
        <li>Ne jamais transmettre de mot de passe, même à un "support technique"</li>
        <li>Signaler tout comportement suspect à votre équipe sécurité</li>
      </ul>
    `,
  },

  bonnes_pratiques: {
    id: "bonnes_pratiques",
    titre: "Bonnes pratiques : mots de passe et hygiène numérique",
    resume: "Les réflexes simples qui réduisent drastiquement votre exposition aux risques.",
    corpsHtml: `
      <h2>Pourquoi l'hygiène numérique est essentielle</h2>
      <p>La majorité des compromissions de comptes proviennent de mots de passe faibles,
      réutilisés, ou obtenus via des fuites de données publiques.</p>
      <h3>Recommandations essentielles</h3>
      <ul>
        <li>Utilisez un mot de passe unique et complexe par service</li>
        <li>Privilégiez un gestionnaire de mots de passe plutôt que de les mémoriser</li>
        <li>Activez la double authentification (2FA) sur tous les comptes sensibles</li>
        <li>Ne partagez jamais vos identifiants, même en interne</li>
        <li>Vérifiez régulièrement si vos adresses email apparaissent dans des fuites connues</li>
      </ul>
    `,
  },
};

module.exports = ARTICLES;
