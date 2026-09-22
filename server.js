/**
 * LOUPEURL MAIL API - VERSION SMTP GMAIL DIRECT
 * ===============================================
 * Envoie des emails en utilisant directement le compte Gmail
 * (loupeurl404@gmail.com) via le module Nodemailer.
 * AUCUNE configuration Google Cloud requise.
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const nodemailer = require('nodemailer');
const ARTICLES = require('./articles');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;

// ====================
// CONFIGURATION SMTP GMAIL
// ====================
const USER_EMAIL = process.env.MAIL_FROM_EMAIL || 'loupeurl404@gmail.com';
const USER_PASSWORD = process.env.GMAIL_APP_PASSWORD || 'TON_MOT_DE_PASSE_APP_16_CARACTERES'; // ⚠️ OBLIGATOIRE
const SENDER_DISPLAY_NAME = process.env.MAIL_FROM_NAME || 'LoupeURL Sécurité';

// Création du transporteur (le "serveur" d'envoi)
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: USER_EMAIL,
        pass: USER_PASSWORD
    }
});

// Vérification de la configuration
transporter.verify((error, success) => {
    if (error) {
        console.error('❌ Erreur de connexion Gmail :', error.message);
    } else {
        console.log(`✅ Serveur prêt. Expéditeur : ${SENDER_DISPLAY_NAME} <${USER_EMAIL}>`);
    }
});

// ====================
// FONCTION D'ENVOI
// ====================
async function envoyerEmail({ to, subject, html }) {
    try {
        const info = await transporter.sendMail({
            from: `"${SENDER_DISPLAY_NAME}" <${USER_EMAIL}>`, // Le nom de l'entreprise
            to: to,
            subject: subject,
            html: html
        });
        console.log(`✅ Email envoyé à ${to} : ${info.messageId}`);
        return { success: true };
    } catch (error) {
        throw new Error(error.message);
    }
}

// ====================
// TEMPLATE EMAIL
// ====================
function buildEmailWrapper({ titre, contenuHtml, footerNote }) {
  return `
  <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:640px;margin:0 auto;background:#f4f6fb;padding:24px;">
    <div style="background:linear-gradient(135deg,#ef4444,#dc2626);border-radius:14px 14px 0 0;padding:24px 32px;">
      <div style="color:white;font-size:22px;font-weight:800;">🔍 LoupeURL</div>
      <div style="color:#fecaca;font-size:12px;letter-spacing:1px;text-transform:uppercase;margin-top:2px;">
        Sécurité &amp; sensibilisation
      </div>
    </div>
    <div style="background:white;padding:32px;border-radius:0 0 14px 14px;box-shadow:0 4px 20px rgba(0,0,0,0.05);">
      <h1 style="font-size:19px;color:#0f172a;margin-top:0;">${titre}</h1>
      <div style="color:#334155;font-size:14.5px;line-height:1.65;">
        ${contenuHtml}
      </div>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0 16px;">
      <p style="font-size:11.5px;color:#94a3b8;">
        ${footerNote || "Ce message vous est envoyé par LoupeURL dans le cadre d'une campagne de sensibilisation à la cybersécurité."}
      </p>
    </div>
    <div style="text-align:center;color:#94a3b8;font-size:11px;margin-top:16px;">
      © ${new Date().getFullYear()} LoupeURL · Détection intelligente des URL malveillantes
    </div>
  </div>`;
}

// ====================
// ROUTES API
// ====================

// ROUTE 1 : Liste des articles
app.get('/api/articles', (req, res) => {
  const liste = Object.values(ARTICLES).map(({ id, titre, resume }) => ({ id, titre, resume }));
  res.json({ articles: liste });
});

// ROUTE 2 : Envoi d'une campagne (Plusieurs destinataires)
app.post('/api/send-sensibilisation', async (req, res) => {
  const { recipients, articleId } = req.body;

  if (!Array.isArray(recipients) || recipients.length === 0) {
    return res.status(400).json({ error: 'Aucun destinataire fourni.' });
  }
  const article = ARTICLES[articleId];
  if (!article) {
    return res.status(400).json({ error: `Article inconnu : ${articleId}` });
  }

  const html = buildEmailWrapper({
    titre: article.titre,
    contenuHtml: article.corpsHtml,
  });

  const resultats = [];
  // On envoie à chaque destinataire un par un (Gmail limite à 500/jour)
  for (const dest of recipients) {
    try {
      await envoyerEmail({
        to: dest,
        subject: `[Sensibilisation LoupeURL] ${article.titre}`,
        html,
      });
      resultats.push({ email: dest, statut: 'envoyé' });
    } catch (err) {
      resultats.push({ email: dest, statut: 'échec', erreur: err.message });
    }
  }

  const echecs = resultats.filter(r => r.statut === 'échec');
  res.json({
    total: recipients.length,
    envoyes: resultats.length - echecs.length,
    echecs: echecs.length,
    details: resultats,
  });
});

// ROUTE 3 : Alerte automatique
app.post('/api/send-alert', async (req, res) => {
  const { recipients, url, probabilite, niveau } = req.body;

  if (!Array.isArray(recipients) || recipients.length === 0) {
    return res.status(400).json({ error: 'Aucun destinataire fourni.' });
  }
  if (!url) {
    return res.status(400).json({ error: 'URL manquante.' });
  }

  const contenuHtml = `
    <p>Une URL a été identifiée comme <strong>potentiellement malveillante</strong> par le
    moteur de détection LoupeURL.</p>
    <div style="background:#fef2f2;border-left:4px solid #ef4444;padding:14px 18px;border-radius:8px;margin:16px 0;">
      <div style="font-size:13px;color:#991b1b;font-weight:600;">URL analysée</div>
      <div style="font-size:13.5px;color:#7f1d1d;word-break:break-all;margin-top:4px;">${url}</div>
    </div>
    <ul>
      <li><strong>Probabilité de malveillance :</strong> ${probabilite ?? '—'}%</li>
      <li><strong>Niveau de risque :</strong> ${niveau ?? '—'}</li>
    </ul>
    <p>Nous vous recommandons de <strong>ne pas cliquer sur ce lien</strong> et de le signaler
    à votre équipe sécurité si vous l'avez reçu par email ou message.</p>
  `;

  const html = buildEmailWrapper({
    titre: '🚨 Alerte URL suspecte détectée',
    contenuHtml,
    footerNote: "Cette alerte automatique est envoyée par le système de détection LoupeURL.",
  });

  const resultats = [];
  for (const dest of recipients) {
    try {
      await envoyerEmail({
        to: dest,
        subject: '🚨 [LoupeURL] Alerte — URL malveillante détectée',
        html,
      });
      resultats.push({ email: dest, statut: 'envoyé' });
    } catch (err) {
      resultats.push({ email: dest, statut: 'échec', erreur: err.message });
    }
  }

  res.json({ total: recipients.length, details: resultats });
});

// ====================
// LANCEMENT
// ====================
app.listen(PORT, () => {
  console.log(`🚀 LoupeURL Mail API (SMTP Direct) démarrée sur http://localhost:${PORT}`);
});