"""Conexão com o banco de dados.

Usamos SQLite (um arquivo local, já vem com o Python).
Para trocar por PostgreSQL depois, basta mudar a DATABASE_URL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./equipamentos.db"

# check_same_thread=False: necessário só no SQLite, porque o FastAPI
# pode atender requisições em threads diferentes.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Classe base de todas as tabelas (models)."""


def get_db():
    """Abre uma sessão por requisição e garante que ela seja fechada no fim."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
