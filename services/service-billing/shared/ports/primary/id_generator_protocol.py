from abc import ABC, abstractmethod
from typing import Any

class IdGeneratorProtocol(ABC):
    """
    Port primaire pour la génération d'identifiants.
    Cette interface définit comment les identifiants doivent être générés.
    """
    
    @abstractmethod
    def generate_id(self) -> Any:
        """
        Génère un nouvel identifiant unique.
        
        Returns:
            Any: Un identifiant unique, généralement un UUID
        """
        pass