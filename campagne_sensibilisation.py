"""
CAMPAGNE DE SENSIBILISATION - Envoi massif d'emails éducatifs
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from datetime import datetime
import pandas as pd
import random

class CampagneSensibilisation:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = None
        self.password = None
        
    def set_credentials(self, email, password):
        self.email = email
        self.password = password
    
    def generer_email_sensibilisation(self, destinataire):
        """Génère un email de sensibilisation personnalisé"""
        
        types_attaque = [
            {
                "nom": "Phishing (hameçonnage)",
                "description": "Les cybercriminels se font passer pour une entreprise légitime pour voler vos identifiants.",
                "exemple": "exemple@banque-securisee.com",
                "conseil": "Vérifiez toujours l'URL complète avant de saisir des informations personnelles."
            },
            {
                "nom": "URL malveillante",
                "description": "Des liens piégés vous redirigent vers des sites infectés.",
                "exemple": "http://192.168.1.105/login",
                "conseil": "Survolez les liens avant de cliquer pour voir leur destination réelle."
            },
            {
                "nom": "Ingénierie sociale",
                "description": "Les attaquants manipulent psychologiquement les victimes.",
                "exemple": "Appel téléphonique urgent demandant vos identifiants",
                "conseil": "Ne communiquez jamais d'informations sensibles par téléphone ou email."
            }
        ]
        
        attaque = random.choice(types_attaque)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e3a5f, #2d5a87); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
                .danger-box {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 15px 0; }}
                .success-box {{ background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; }}
                .tip {{ background: #cce5ff; border-left: 4px solid #007bff; padding: 15px; margin: 15px 0; }}
                .button {{ background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .footer {{ text-align: center; padding: 20px; font-size: 0.8em; color: #6c757d; margin-top: 20px; }}
                h2 {{ color: #1e3a5f; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ Sécurité Informatique</h1>
                <p>Protégez-vous contre les menaces en ligne</p>
            </div>
            
            <div class="content">
                <h2>Bonjour {destinataire.split('@')[0]} 👋</h2>
                
                <div class="success-box">
                    <strong>✅ Saviez-vous ?</strong>
                    <p>Les attaques par URL malveillantes sont en augmentation de 40% cette année.</p>
                </div>
                
                <h3>🎯 Cette semaine : {attaque['nom']}</h3>
                <p>{attaque['description']}</p>
                
                <div class="danger-box">
                    <strong>⚠️ Exemple courant :</strong>
                    <p>{attaque['exemple']}</p>
                </div>
                
                <div class="tip">
                    <strong>💡 Conseil sécurité :</strong>
                    <p>{attaque['conseil']}</p>
                </div>
                
                <h3>📋 Vérification en 3 étapes :</h3>
                <ol>
                    <li><strong>Vérifiez le domaine</strong> - L'URL contient-elle le bon nom de domaine ?</li>
                    <li><strong>Survolez les liens</strong> - Où mène vraiment le lien ?</li>
                    <li><strong>Méfiez-vous de l'urgence</strong> - Les attaquants pressent leurs victimes</li>
                </ol>
                
                <div class="alert-box">
                    <strong>🔑 Rappel important :</strong>
                    <p>Jamais d'identifiants, jamais de mots de passe, jamais de coordonnées bancaires par email.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="#" style="background: #dc3545; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        🚨 Signaler un lien suspect
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>Cet email fait partie d'une campagne de sensibilisation à la sécurité informatique.</p>
                <p>Pour vous désinscrire, répondez à cet email avec "STOP" en objet.</p>
                <p>© 2026 - Détection d'URL Malveillantes</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def envoyer_campagne(self, destinataires, objet="[SENSIBILISATION] Protégez-vous des URL malveillantes"):
        """Envoyer une campagne de sensibilisation à une liste de destinataires"""
        if not self.email or not self.password:
            return False, "Identifiants email non configurés"
        
        if not destinataires:
            return False, "Aucun destinataire spécifié"
        
        success_count = 0
        failed = []
        
        for destinataire in destinataires:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.email
                msg['To'] = destinataire
                msg['Subject'] = objet
                
                # Contenu HTML
                html_content = self.generer_email_sensibilisation(destinataire)
                msg.attach(MIMEText(html_content, 'html'))
                
                # Envoyer
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                server.quit()
                
                success_count += 1
                
            except Exception as e:
                failed.append((destinataire, str(e)))
        
        return success_count, failed