import pytest
from datetime import timedelta
import os
from dotenv import load_dotenv
from jose import jwt

from shared.services.authenticator.basic_authenticator import BasicAuthenticator

# Charger les variables d'environnement
load_dotenv()

@pytest.fixture
def authenticator():
    """Fixture pour créer une instance de BasicAuthenticator pour les tests"""
    return BasicAuthenticator()

def test_password_hashing(authenticator):
    """Test le hash et la vérification des mots de passe"""
    # Arrange
    password = "test_password"
    
    # Act
    hashed_password = authenticator.get_password_hash(password)
    result = authenticator.verify_password(password, hashed_password)
    
    # Assert
    assert result is True
    assert authenticator.verify_password("wrong_password", hashed_password) is False

def test_jwt_token_creation(authenticator):
    """Test la création de tokens JWT"""
    # Arrange
    data = {"sub": "test@example.com", "role": "admin"}
    expires_delta = timedelta(minutes=15)
    
    # Act
    token = authenticator.create_access_token(data, expires_delta)
    
    # Assert
    assert token is not None
    assert isinstance(token, str)
    
    # Vérifier que le token peut être décodé avec la clé secrète
    payload = jwt.decode(
        token, 
        os.getenv("JWT_SECRET_KEY", "default_secret_key"), 
        algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
    )
    
    assert payload["sub"] == "test@example.com"
    assert payload["role"] == "admin"
    assert "exp" in payload