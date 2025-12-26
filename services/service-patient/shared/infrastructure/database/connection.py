# medisecure-backend/shared/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import logging
from typing import AsyncGenerator

from shared.infrastructure.config.settings import get_settings

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupérer les settings centralisées
settings = get_settings()

# Configuration optimisée du moteur asynchrone
engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=True,  # Vérifier la connexion avant de l'utiliser
    pool_recycle=settings.database.pool_recycle,  # Recycler les connexions
    # Optimisations pour les performances async
    future=True,  # Utiliser la nouvelle API SQLAlchemy 2.0
    # Pour les tests, on peut utiliser NullPool pour éviter les problèmes de concurrence
    poolclass=NullPool if settings.testing else None,
)

# Création de la session asynchrone optimisée
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Important pour async : ne pas expirer les objets après commit
)

# Classe de base pour les modèles
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Fournit une session de base de données asynchrone optimisée.
    
    Utilise un gestionnaire de contexte pour assurer la fermeture
    propre de la session et la gestion des transactions.
    
    Yields:
        AsyncSession: Session de base de données asynchrone
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # En cas d'erreur, rollback automatique
            await session.rollback()
            raise
        finally:
            # Fermeture automatique de la session
            await session.close()

# Factory pour créer des sessions (utilisée par le container)
def create_async_session_factory():
    """
    Factory pour créer des sessions asynchrones.
    Utilisée par le container d'injection de dépendances.
    """
    return AsyncSessionLocal

# Fonction utilitaire pour les tests
async def create_test_session() -> AsyncSession:
    """
    Crée une session pour les tests.
    
    Returns:
        AsyncSession: Session de test
    """
    if not settings.testing:
        logger.warning("create_test_session() appelée en dehors du contexte de test")
    
    return AsyncSessionLocal()

# Log de la configuration au démarrage
def log_database_config():
    """Log la configuration de base de données de manière sécurisée"""
    db_url = settings.get_database_url()
    safe_url = db_url.split('@')[0] + ":***@" + (db_url.split('@')[1] if '@' in db_url else 'N/A')
    
    logger.info(f"=== Configuration Base de Données ===")
    logger.info(f"URL: {safe_url}")
    logger.info(f"Driver: asyncpg (PostgreSQL async)")
    logger.info(f"Pool size: {settings.database.pool_size}")
    logger.info(f"Max overflow: {settings.database.max_overflow}")
    logger.info(f"Pool recycle: {settings.database.pool_recycle}s")
    logger.info(f"Echo SQL: {settings.database.echo}")
    logger.info(f"Testing mode: {settings.testing}")

# Initialiser la configuration au moment de l'import
log_database_config()