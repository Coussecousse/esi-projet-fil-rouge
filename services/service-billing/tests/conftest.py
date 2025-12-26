import pytest
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import Generator, Any

from shared.infrastructure.database.connection import Base
from shared.container.container import Container

# Charger les variables d'environnement
load_dotenv()

# Utiliser une base de données de test
TEST_DATABASE_URL = os.getenv("DATABASE_TEST_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/medisecure_test")

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Créer une nouvelle boucle d'événements pour chaque session de test"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Créer le moteur SQLAlchemy pour les tests"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Créer les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Supprimer les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Fermer le moteur
    await engine.dispose()

@pytest.fixture(scope="function")
async def session(engine) -> AsyncSession:
    """Créer une session SQLAlchemy pour les tests"""
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
def container() -> Container:
    """Créer un container d'injection de dépendances pour les tests"""
    container = Container()
    container.config.database_url.override(TEST_DATABASE_URL)
    container.config.environment.override("test")
    
    # Utiliser le repository en mémoire pour les tests
    container.user_repository.override(container.user_repository_in_memory)
    
    return container