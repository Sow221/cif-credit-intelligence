"""Rate limiting de l'API (slowapi).

Protège chaque endpoint avec des limites par minute issues des settings
(voir Partie 3.1 : contrats d'API complets). Le client est identifié par
son adresse IP via slowapi.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config.settings import Settings

limiter = Limiter(key_func=get_remote_address)

_settings = Settings()


def get_limit(rate_name: str) -> str:
    """Construit la chaine slowapi `N/minute` depuis un taux des settings.

    Args:
        rate_name: nom de l'attribut settings (ex. ``rate_drift``).

    Returns:
        Chaine comme ``"5/minute"``.
    """
    return f"{getattr(_settings, rate_name)}/minute"