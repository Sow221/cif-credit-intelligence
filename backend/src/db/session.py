"""Acces a la base de donnees via SQLAlchemy.

Definit le moteur (engine), la session et la base declarative partages.
Le pilote utilise est psycopg (v3) : `postgresql+psycopg://`.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config.settings import Settings

settings = Settings()

engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Dependance FastAPI fournissant une session de base de donnees."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()