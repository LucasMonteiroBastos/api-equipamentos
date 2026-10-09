"""Testes automatizados do CRUD.

Cada teste usa um banco SQLite em memória, novo e vazio,
para não mexer no banco "de verdade" (equipamentos.db).
Rodar:  pytest -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def get_db_teste():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_teste  # troca o banco só durante o teste
    yield TestClient(app)
    app.dependency_overrides.clear()


BRITADOR = {"tag": "BR-2001-01", "nome": "Britador cônico", "tipo": "britador"}


def test_criar(client):
    r = client.post("/equipamentos", json=BRITADOR)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["id"] == 1
    assert corpo["status"] == "operando"  # valor padrão


def test_tag_duplicada_retorna_409(client):
    client.post("/equipamentos", json=BRITADOR)
    r = client.post("/equipamentos", json=BRITADOR)
    assert r.status_code == 409


def test_status_invalido_retorna_422(client):
    r = client.post("/equipamentos", json={**BRITADOR, "status": "quebrado"})
    assert r.status_code == 422


def test_listar_e_filtrar(client):
    client.post("/equipamentos", json=BRITADOR)
    client.post("/equipamentos", json={"tag": "TC-01", "nome": "Correia", "tipo": "correia",
                                       "status": "manutencao"})
    assert len(client.get("/equipamentos").json()) == 2
    em_manutencao = client.get("/equipamentos", params={"status": "manutencao"}).json()
    assert [e["tag"] for e in em_manutencao] == ["TC-01"]


def test_obter_inexistente_retorna_404(client):
    assert client.get("/equipamentos/999").status_code == 404


def test_atualizar_parcial(client):
    client.post("/equipamentos", json=BRITADOR)
    r = client.patch("/equipamentos/1", json={"status": "manutencao"})
    assert r.status_code == 200
    assert r.json()["status"] == "manutencao"
    assert r.json()["nome"] == "Britador cônico"  # o resto não mudou


@pytest.mark.parametrize("rota", ["/", "/simulador"])
def test_paginas_html(client, rota):
    r = client.get(rota)
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_remover(client):
    client.post("/equipamentos", json=BRITADOR)
    assert client.delete("/equipamentos/1").status_code == 204
    assert client.get("/equipamentos/1").status_code == 404
