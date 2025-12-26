from abc import ABC, abstractmethod
from typing import List, Optional

class MailerProtocol(ABC):
    """
    Port secondaire pour l'envoi d'emails.
    Cette interface définit comment les emails doivent être envoyés.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe.
        
        Args:
            to_email: L'adresse email du destinataire
            reset_token: Le token de réinitialisation de mot de passe
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        pass
    
    @abstractmethod
    async def send_confirmation_email(self, to_email: str, confirmation_token: str) -> bool:
        """
        Envoie un email de confirmation d'inscription.
        
        Args:
            to_email: L'adresse email du destinataire
            confirmation_token: Le token de confirmation d'inscription
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        pass