# shared/infrastructure/config/settings.py
from pydantic import BaseSettings, Field, validator
from typing import List, Optional
import os
from pathlib import Path


class DatabaseSettings(BaseSettings):
    """Configuration de la base de données"""
    
    url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/medisecure",
        env="DATABASE_URL",
        description="URL de connexion à la base de données"
    )
    
    test_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/medisecure_test",
        env="DATABASE_TEST_URL",
        description="URL de connexion à la base de données de test"
    )
    
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    @validator("url", pre=True)
    def ensure_asyncpg_driver(cls, v):
        """S'assurer que l'URL utilise le driver asyncpg"""
        if "postgresql://" in v and "asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        
        # Auto-détection de l'environnement Kubernetes
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            v = v.replace("@localhost:", "@db-service:")
        # Auto-détection de l'environnement Docker
        elif os.getenv("ENVIRONMENT") == "docker" or os.path.exists("/.dockerenv"):
            v = v.replace("@localhost:", "@medisecure-db:")
        
        return v


class SecuritySettings(BaseSettings):
    """Configuration de sécurité et JWT"""
    
    jwt_secret_key: str = Field(
        default="your-secret-key-here-change-in-production-PLEASE",
        env="JWT_SECRET_KEY",
        description="Clé secrète pour signer les tokens JWT"
    )
    
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    access_token_expire_minutes: int = Field(
        default=30, 
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v):
        """Valider la clé secrète JWT"""
        if v == "your-secret-key-here-change-in-production-PLEASE":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("JWT_SECRET_KEY must be set in production!")
        
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        
        return v


class ServerSettings(BaseSettings):
    """Configuration du serveur"""
    
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000", 
            "http://localhost:3001",
            "http://localhost",
            "http://frontend",
            "http://frontend-service:3001",
            "http://frontend-service:3000"
        ],
        env="CORS_ORIGINS"
    )
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parser la liste des origines CORS depuis une string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("debug", pre=True)
    def set_debug_from_environment(cls, v, values):
        """Activer le debug automatiquement en développement"""
        environment = values.get("environment", "development")
        if environment == "development":
            return True
        return v


class LoggingSettings(BaseSettings):
    """Configuration des logs"""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Logs structurés pour production
    json_logs: bool = Field(default=False, env="JSON_LOGS")
    
    @validator("json_logs", pre=True) 
    def enable_json_logs_in_production(cls, v, values):
        """Activer les logs JSON en production"""
        if values.get("environment") == "production":
            return True
        return v


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # Métadonnées de l'application
    app_name: str = Field(default="MediSecure API", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    description: str = Field(
        default="API pour la gestion des dossiers patients et des rendez-vous médicaux",
        env="APP_DESCRIPTION"
    )
    
    # Sous-configurations
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    server: ServerSettings = ServerSettings()
    logging: LoggingSettings = LoggingSettings()
    
    # Configuration de test
    testing: bool = Field(default=False, env="TESTING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Permettre les variables imbriquées comme DATABASE__URL
        env_nested_delimiter = "__"
        case_sensitive = False
    
    @validator("*", pre=True)
    def empty_str_to_none(cls, v):
        """Convertir les chaînes vides en None"""
        if v == "":
            return None
        return v
    
    def get_database_url(self) -> str:
        """Obtenir l'URL de base de données appropriée"""
        if self.testing:
            return self.database.test_url
        return self.database.url
    
    def is_development(self) -> bool:
        """Vérifier si on est en mode développement"""
        return self.server.environment == "development"
    
    def is_production(self) -> bool:
        """Vérifier si on est en mode production"""
        return self.server.environment == "production"


# Instance globale des settings
settings = Settings()

# Fonction helper pour obtenir les settings
def get_settings() -> Settings:
    """Obtenir l'instance des settings"""
    return settings

# Fonction pour recharger les settings (utile pour les tests)
def reload_settings() -> Settings:
    """Recharger les settings depuis les variables d'environnement"""
    global settings
    settings = Settings()
    return settings