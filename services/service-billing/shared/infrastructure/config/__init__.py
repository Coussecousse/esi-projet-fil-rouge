# shared/infrastructure/config/__init__.py
"""
Module de configuration centralisée pour MediSecure.

Ce module fournit une configuration type-safe et validée 
pour toute l'application en utilisant pydantic-settings.
"""

from .settings import settings, get_settings, reload_settings, Settings

__all__ = ["settings", "get_settings", "reload_settings", "Settings"]