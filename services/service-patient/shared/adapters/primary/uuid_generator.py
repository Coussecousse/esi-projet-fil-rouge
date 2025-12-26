import uuid
from shared.ports.primary.id_generator_protocol import IdGeneratorProtocol

class UuidGenerator(IdGeneratorProtocol):
    """
    Adaptateur primaire pour la génération d'identifiants UUID.
    Implémente le port IdGeneratorProtocol.
    """
    
    def generate_id(self) -> uuid.UUID:
        """
        Génère un nouvel identifiant UUID.
        
        Returns:
            uuid.UUID: Un identifiant UUID v4 généré aléatoirement
        """
        return uuid.uuid4()