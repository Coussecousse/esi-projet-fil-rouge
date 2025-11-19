# shared/infrastructure/monitoring/health_checker.py
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Statuts de santé possibles"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Représente une vérification de santé individuelle"""
    
    def __init__(self, name: str, status: HealthStatus, details: Dict[str, Any] = None):
        self.name = name
        self.status = status
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.response_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour la sérialisation"""
        return {
            "name": self.name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms,
            "details": self.details
        }


class HealthChecker:
    """Service de vérification de la santé de l'application"""
    
    def __init__(self):
        self.settings = get_settings()
        self.checks: List[HealthCheck] = []
    
    async def check_database(self, session: AsyncSession) -> HealthCheck:
        """Vérifier la connectivité à la base de données"""
        start_time = datetime.utcnow()
        
        try:
            # Test de connexion simple
            await session.execute(text("SELECT 1"))
            
            # Test des tables principales
            tables_check = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'patients', 'appointments')
            """))
            existing_tables = [row[0] for row in tables_check.fetchall()]
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if len(existing_tables) >= 3:
                status = HealthStatus.HEALTHY
                details = {
                    "connection": "OK",
                    "tables": existing_tables,
                    "database_url": self._mask_db_url()
                }
            else:
                status = HealthStatus.DEGRADED
                details = {
                    "connection": "OK",
                    "tables": existing_tables,
                    "missing_tables": list(set(['users', 'patients', 'appointments']) - set(existing_tables)),
                    "database_url": self._mask_db_url()
                }
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            status = HealthStatus.UNHEALTHY
            details = {
                "connection": "FAILED",
                "error": str(e),
                "database_url": self._mask_db_url()
            }
        
        check = HealthCheck("database", status, details)
        check.response_time_ms = response_time
        return check
    
    def check_configuration(self) -> HealthCheck:
        """Vérifier la configuration de l'application"""
        details = {}
        status = HealthStatus.HEALTHY
        
        # Vérifier les variables critiques
        critical_settings = {
            "jwt_secret_key": self.settings.security.jwt_secret_key,
            "database_url": self.settings.get_database_url(),
            "environment": self.settings.server.environment
        }
        
        for key, value in critical_settings.items():
            if not value or (key == "jwt_secret_key" and value == "your-secret-key-here-change-in-production-PLEASE"):
                status = HealthStatus.UNHEALTHY
                details[f"{key}_status"] = "MISSING or DEFAULT"
            else:
                details[f"{key}_status"] = "OK"
        
        # Informations additionnelles
        details.update({
            "app_version": self.settings.version,
            "environment": self.settings.server.environment,
            "debug_mode": self.settings.server.debug,
            "cors_origins_count": len(self.settings.server.cors_origins)
        })
        
        return HealthCheck("configuration", status, details)
    
    def check_memory_and_performance(self) -> HealthCheck:
        """Vérifier la mémoire et les performances basiques"""
        try:
            import psutil
            
            # Informations mémoire
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            details = {
                "memory_used_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_used_percent": disk.percent,
                "disk_free_gb": disk.free // (1024 * 1024 * 1024)
            }
            
            # Déterminer le statut basé sur l'usage
            if memory.percent > 90 or disk.percent > 95:
                status = HealthStatus.UNHEALTHY
            elif memory.percent > 75 or disk.percent > 80:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
                
        except ImportError:
            # psutil non disponible
            details = {"note": "psutil not available, basic check only"}
            status = HealthStatus.HEALTHY
        except Exception as e:
            details = {"error": str(e)}
            status = HealthStatus.DEGRADED
        
        return HealthCheck("system", status, details)
    
    async def run_all_checks(self, session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """Exécuter toutes les vérifications de santé"""
        self.checks = []
        
        # Check 1: Configuration
        config_check = self.check_configuration()
        self.checks.append(config_check)
        
        # Check 2: Base de données (si session fournie)
        if session:
            db_check = await self.check_database(session)
            self.checks.append(db_check)
        
        # Check 3: Système
        system_check = self.check_memory_and_performance()
        self.checks.append(system_check)
        
        # Déterminer le statut global
        overall_status = self._determine_overall_status()
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.settings.version,
            "environment": self.settings.server.environment,
            "checks": [check.to_dict() for check in self.checks],
            "summary": self._get_summary()
        }
    
    def _determine_overall_status(self) -> HealthStatus:
        """Déterminer le statut global basé sur tous les checks"""
        if not self.checks:
            return HealthStatus.UNHEALTHY
        
        # Si au moins un check est UNHEALTHY, l'ensemble est UNHEALTHY
        if any(check.status == HealthStatus.UNHEALTHY for check in self.checks):
            return HealthStatus.UNHEALTHY
        
        # Si au moins un check est DEGRADED, l'ensemble est DEGRADED
        if any(check.status == HealthStatus.DEGRADED for check in self.checks):
            return HealthStatus.DEGRADED
        
        # Sinon, tout va bien
        return HealthStatus.HEALTHY
    
    def _get_summary(self) -> Dict[str, int]:
        """Obtenir un résumé des statuts"""
        summary = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "total": len(self.checks)
        }
        
        for check in self.checks:
            if check.status == HealthStatus.HEALTHY:
                summary["healthy"] += 1
            elif check.status == HealthStatus.DEGRADED:
                summary["degraded"] += 1
            elif check.status == HealthStatus.UNHEALTHY:
                summary["unhealthy"] += 1
        
        return summary
    
    def _mask_db_url(self) -> str:
        """Masquer le mot de passe dans l'URL de base de données pour les logs"""
        url = self.settings.get_database_url()
        if "@" in url:
            protocol_and_auth, host_and_db = url.split("@", 1)
            if ":" in protocol_and_auth:
                protocol_user, _ = protocol_and_auth.rsplit(":", 1)
                return f"{protocol_user}:***@{host_and_db}"
        return url