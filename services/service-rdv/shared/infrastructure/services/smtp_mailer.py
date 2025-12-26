import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv

from shared.ports.secondary.mailer_protocol import MailerProtocol

# Charger les variables d'environnement
load_dotenv()

class SmtpMailer(MailerProtocol):
    """
    Adaptateur secondaire pour l'envoi d'emails via SMTP.
    Implémente le port MailerProtocol.
    """
    
    def __init__(self):
        """
        Initialise le mailer avec les paramètres SMTP depuis les variables d'environnement.
        """
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.example.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "user@example.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "your_password_here")
        self.email_from = os.getenv("EMAIL_FROM", "noreply@medisecure.com")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Envoie un email.
        
        Args:
            to_email: L'adresse email du destinataire
            subject: Le sujet de l'email
            body: Le corps de l'email en texte brut
            cc: Les adresses email en copie (optionnel)
            bcc: Les adresses email en copie cachée (optionnel)
            html_body: Le corps de l'email en HTML (optionnel)
            attachments: Les pièces jointes (optionnel)
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = to_email
            
            # Ajouter les destinataires en copie
            if cc:
                message["Cc"] = ", ".join(cc)
            
            # Ajouter le corps en texte brut
            part1 = MIMEText(body, "plain")
            message.attach(part1)
            
            # Ajouter le corps en HTML s'il est fourni
            if html_body:
                part2 = MIMEText(html_body, "html")
                message.attach(part2)
            
            # Établir la connexion SMTP et envoyer l'email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                # Démarrer le chiffrement TLS
                server.starttls()
                
                # Connexion au serveur SMTP
                server.login(self.smtp_user, self.smtp_password)
                
                # Préparer la liste complète des destinataires
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                # Envoyer l'email
                server.sendmail(self.email_from, recipients, message.as_string())
            
            return True
        
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False
    
    async def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe.
        
        Args:
            to_email: L'adresse email du destinataire
            reset_token: Le token de réinitialisation de mot de passe
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        subject = "Réinitialisation de votre mot de passe MediSecure"
        
        # Corps en texte brut
        body = f"""
        Bonjour,
        
        Vous avez demandé la réinitialisation de votre mot de passe sur MediSecure.
        
        Veuillez cliquer sur le lien suivant pour réinitialiser votre mot de passe:
        {os.getenv('FRONTEND_URL', 'https://medisecure.com')}/reset-password?token={reset_token}
        
        Si vous n'avez pas fait cette demande, vous pouvez ignorer cet email.
        
        Cordialement,
        L'équipe MediSecure
        """
        
        # Corps en HTML
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4285f4; color: #ffffff; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background-color: #4285f4; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Réinitialisation de mot de passe</h1>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>Vous avez demandé la réinitialisation de votre mot de passe sur MediSecure.</p>
                    <p>Veuillez cliquer sur le bouton ci-dessous pour réinitialiser votre mot de passe:</p>
                    <p style="text-align: center;">
                        <a href="{os.getenv('FRONTEND_URL', 'https://medisecure.com')}/reset-password?token={reset_token}" class="button">Réinitialiser mon mot de passe</a>
                    </p>
                    <p>Si vous n'avez pas fait cette demande, vous pouvez ignorer cet email.</p>
                    <p>Cordialement,<br>L'équipe MediSecure</p>
                </div>
                <div class="footer">
                    <p>Ce message a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_confirmation_email(self, to_email: str, confirmation_token: str) -> bool:
        """
        Envoie un email de confirmation d'inscription.
        
        Args:
            to_email: L'adresse email du destinataire
            confirmation_token: Le token de confirmation d'inscription
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        subject = "Confirmez votre inscription sur MediSecure"
        
        # Corps en texte brut
        body = f"""
        Bonjour,
        
        Merci de vous être inscrit sur MediSecure.
        
        Veuillez cliquer sur le lien suivant pour confirmer votre adresse email:
        {os.getenv('FRONTEND_URL', 'https://medisecure.com')}/confirm-email?token={confirmation_token}
        
        Si vous n'avez pas fait cette demande, vous pouvez ignorer cet email.
        
        Cordialement,
        L'équipe MediSecure
        """
        
        # Corps en HTML
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4285f4; color: #ffffff; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background-color: #4285f4; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirmation d'inscription</h1>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>Merci de vous être inscrit sur MediSecure.</p>
                    <p>Veuillez cliquer sur le bouton ci-dessous pour confirmer votre adresse email:</p>
                    <p style="text-align: center;">
                        <a href="{os.getenv('FRONTEND_URL', 'https://medisecure.com')}/confirm-email?token={confirmation_token}" class="button">Confirmer mon email</a>
                    </p>
                    <p>Si vous n'avez pas fait cette demande, vous pouvez ignorer cet email.</p>
                    <p>Cordialement,<br>L'équipe MediSecure</p>
                </div>
                <div class="footer">
                    <p>Ce message a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )