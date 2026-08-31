"""Configuration centralisee (P0).

Re-exporte la classe Settings existante (src.config.settings) comme source
unique de configuration, conformement a la structure cible src/core/config.py.
"""

from functools import lru_cache

from src.config.settings import Settings


@lru_cache
def get_settings() -> Settings:
    """Retourne l'instance de configuration en cache."""
    return Settings()


__all__ = ["Settings", "get_settings"]
