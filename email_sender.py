"""
EMAIL_SENDER - Envoi de rapports d'URL malveillantes par email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from fpdf import FPDF
import re

class EmailReporter:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = None
        self.password = None
        
    def set_credentials(self, email, password):
        """Configurer les identifiants d'envoi"""
        self.email = email
        self.password = password
        
    def generer_rapport_pdf(self, url, resultat, features=None):
        """Génère un rapport PDF détaillé pour l'URL analysée"""
        pdf = FPDF()
        pdf.add_page()
        
        # En-tête
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(220, 50, 50) if resultat['prediction'] == 1 else pdf.set_text_color(50, 180, 80)
        pdf.cell(0, 15, "RAPPORT D'ANALYSE D'URL", ln=True, align="C")
        
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.cell(0, 10, f"URL analysée: {url[:80]}...", ln=True)
        pdf.ln(5)
        
        # Verdict
        pdf.set_font("Arial", "B", 14)
        if resultat['prediction'] == 1:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 12, f"VERDICT: URL SUSPECTE - {resultat['probabilite']:.0f}% de risque", ln=True)
        else:
            pdf.set_text_color(0, 150, 0)
            pdf.cell(0, 12, f"VERDICT: URL SÛRE - {resultat['probabilite']:.0f}% de risque", ln=True)
        
        pdf.ln(5)
        
        # Détails des caractéristiques
        if features:
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 10, "Caractéristiques analysées:", ln=True)
            pdf.set_font("Arial", "", 10)
            
            caracteristiques_cle = {
                'url_length': 'Longueur URL',
                'num_dots': 'Nombre de points',
                'num_subdomains': 'Sous-domaines',
                'has_ip': 'Adresse IP',
                'suspicious_words': 'Mots suspects',
                'num_special_chars': 'Caractères spéciaux'
            }
            
            for key, label in caracteristiques_cle.items():
                if key in features:
                    valeur = features[key]
                    if key == 'has_ip':
                        valeur = "Oui" if valeur == 1 else "Non"
                    pdf.cell(0, 8, f"  • {label}: {valeur}", ln=True)
        
        # Recommendations
        pdf.ln(8)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(200, 100, 0)
        pdf.cell(0, 10, "RECOMMANDATIONS:", ln=True)
        pdf.set_font("Arial", "", 10)
        
        if resultat['prediction'] == 1:
            pdf.multi_cell(0, 8, "• Ne cliquez pas sur ce lien\n• Ne fournissez aucune information personnelle\n• Signalez cette URL aux autorités compétentes\n• Vérifiez toujours l'URL avant de cliquer")
        else:
            pdf.multi_cell(0, 8, "• Cette URL semble sûre, mais restez vigilant\n• Vérifiez toujours le domaine avant de saisir des informations sensibles")
        
        # Pied de page
        pdf.ln(10)
        pdf.set_font("Arial", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, "Rapport généré automatiquement par l'outil de détection d'URL malveillantes", ln=True)
        
        # Sauvegarder temporairement
        temp_pdf = f"rapport_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(temp_pdf)
        return temp_pdf
    
    def envoyer_rapport(self, destinataire, url, resultat, features=None):
        """Envoyer le rapport d'analyse par email"""
        if not self.email or not self.password:
            return False, "Identifiants email non configurés"
        
        try:
            # Générer le PDF
            pdf_path = self.generer_rapport_pdf(url, resultat, features)
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = destinataire
            msg['Subject'] = f"[ALERTE SECURITE] Rapport d'analyse URL - {datetime.now().strftime('%d/%m/%Y')}"
            
            # Corps du message
            corps = f"""
            Bonjour,
            
            Suite à l'analyse d'une URL, veuillez trouver ci-joint le rapport détaillé.
            
            URL analysée: {url}
            Verdict: {'URL SUSPECTE' if resultat['prediction'] == 1 else 'URL SÛRE'}
            Probabilité de menace: {resultat['probabilite']:.0f}%
            
            Ce rapport a été généré automatiquement par notre système de détection d'URL malveillantes.
            
            Cordialement,
            L'équipe de sécurité
            """
            
            msg.attach(MIMEText(corps, 'plain'))
            
            # Attacher le PDF
            with open(pdf_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename=rapport_url_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
                msg.attach(part)
            
            # Envoyer
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            # Nettoyer
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            return True, "Rapport envoyé avec succès"
            
        except Exception as e:
            return False, f"Erreur d'envoi: {str(e)}"