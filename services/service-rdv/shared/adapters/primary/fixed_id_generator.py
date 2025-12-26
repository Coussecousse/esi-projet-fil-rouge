import uuid
from shared.ports.primary.id_generator_protocol import IdGeneratorProtocol

class FixedIdGenerator(IdGeneratorProtocol):
    """
    Adaptateur primaire pour la génération d'identifiants fixes pour les tests.
    Implémente le port IdGeneratorProtocol.
    """
    
    def __init__(self, fixed_id: str = "00000000-0000-0000-0000-000000000000"):
        """
        Initialise le générateur avec un ID fixe.
        
        Args:
            fixed_id: L'ID fixe à générer (format UUID)
        """
        self.fixed_id = uuid.UUID(fixed_id)
    
    def generate_id(self) -> uuid.UUID:
        """
        Retourne l'identifiant UUID fixe.
        
        Returns:
            uuid.UUID: L'identifiant UUID fixe
        """
        return self.fixed_id