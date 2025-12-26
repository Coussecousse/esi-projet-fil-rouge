# medisecure-backend/shared/container/container.py
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging

from shared.infrastructure.config.settings import get_settings
from shared.adapters.primary.uuid_generator import UuidGenerator
from shared.adapters.secondary.postgres_user_repository import PostgresUserRepository
from shared.adapters.secondary.in_memory_user_repository import InMemoryUserRepository
from shared.infrastructure.services.smtp_mailer import SmtpMailer
from shared.services.authenticator.basic_authenticator import BasicAuthenticator
from shared.application.services.auth_service import AuthenticationService

from patient_management.infrastructure.adapters.secondary.postgres_patient_repository import PostgresPatientRepository
from patient_management.infrastructure.adapters.secondary.in_memory_patient_repository import InMemoryPatientRepository
from patient_management.domain.services.patient_service import PatientService

from appointment_management.infrastructure.adapters.secondary.postgres_appointment_repository import PostgresAppointmentRepository
from appointment_management.infrastructure.adapters.secondary.in_memory_appointment_repository import InMemoryAppointmentRepository
from appointment_management.domain.services.appointment_service import AppointmentService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Container(containers.DeclarativeContainer):
    """
    Container d'injection de dépendances pour l'application.
    Centralise la création et la gestion des instances des différentes classes.
    """
    
    # Récupération des settings centralisées
    settings = providers.Singleton(get_settings)
    
    config = providers.Configuration()
    
    # Log sécurisé de la configuration
    def _log_database_config():
        settings_instance = get_settings()
        db_url = settings_instance.get_database_url()
        safe_url = db_url.split('@')[0] + ":***@" + (db_url.split('@')[1] if '@' in db_url else 'N/A')
        logger.info(f"Database URL configurée: {safe_url}")
        logger.info(f"Environnement: {settings_instance.server.environment}")
        logger.info(f"Mode debug: {settings_instance.server.debug}")
    
    _log_database_config()
    
    # Création du moteur avec configuration centralisée
    engine = providers.Singleton(
        create_async_engine,
        providers.Factory(lambda s: s.get_database_url(), settings),
        echo=providers.Factory(lambda s: s.database.echo or s.server.debug, settings),
        pool_size=providers.Factory(lambda s: s.database.pool_size, settings),
        max_overflow=providers.Factory(lambda s: s.database.max_overflow, settings),
        pool_pre_ping=True,  # Vérifier la connexion avant de l'utiliser
        pool_recycle=providers.Factory(lambda s: s.database.pool_recycle, settings),
    )
    
    # Création de la factory de session
    async_session_factory = providers.Singleton(
        sessionmaker,
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )
    
    # Gestionnaire de contexte pour les sessions
    @asynccontextmanager
    async def get_session():
        async_session = async_session_factory()
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    
    # Adaptateurs primaires
    id_generator = providers.Factory(UuidGenerator)
    authenticator = providers.Factory(BasicAuthenticator)
    
    # Adaptateurs secondaires - Repositories (doivent être définis avant les services qui les utilisent)

    # Pour production :
    user_repository = providers.Factory(
        PostgresUserRepository,
        session_factory=async_session_factory
    )

    patient_repository = providers.Factory(
        PostgresPatientRepository,
        session_factory=async_session_factory
    )

    appointment_repository = providers.Factory(
        PostgresAppointmentRepository,
        session_factory=async_session_factory
    )
    
    # Services d'application
    auth_service = providers.Factory(
        AuthenticationService,
        user_repository=user_repository
    )
    
    # Services du domaine
    patient_service = providers.Factory(PatientService)
    appointment_service = providers.Factory(AppointmentService)
    
    # Repositories en mémoire pour les tests
    user_repository_in_memory = providers.Singleton(InMemoryUserRepository)
    patient_repository_in_memory = providers.Singleton(InMemoryPatientRepository)
    appointment_repository_in_memory = providers.Singleton(InMemoryAppointmentRepository)
    
    # Services d'infrastructure
    mailer = providers.Factory(SmtpMailer)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_instance = get_settings()
        logger.info("Container d'injection de dépendances initialisé")
        logger.info(f"Environnement: {settings_instance.server.environment}")
        logger.info(f"Version de l'app: {settings_instance.version}")
        logger.info(f"Configuration sécurisée: ✅")

# Instance globale du container pour faciliter l'accès
container_instance = None

def get_container():
    """
    Retourne l'instance globale du container.
    Crée une nouvelle instance si elle n'existe pas.
    """
    global container_instance
    if container_instance is None:
        container_instance = Container()
    return container_instance

# Pour les tests
def reset_container():
    """
    Réinitialise le container (utile pour les tests).
    """
    global container_instance
    if container_instance:
        container_instance.shutdown_resources()
    container_instance = None