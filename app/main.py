"""API CRUD de equipamentos.

C - Create  -> POST   /equipamentos
R - Read    -> GET    /equipamentos  e  GET /equipamentos/{id}
U - Update  -> PATCH  /equipamentos/{id}
D - Delete  -> DELETE /equipamentos/{id}

Rodar:  uvicorn app.main:app --reload
Tela:   http://127.0.0.1:8000
Simul.: http://127.0.0.1:8000/simulador
Docs:   http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Equipamento
from app.schemas import EquipamentoAtualizar, EquipamentoCriar, EquipamentoSaida


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas ao iniciar (em projeto maior, usaríamos Alembic para migrations).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="API de Equipamentos", version="1.0.0", lifespan=lifespan)

PASTA_STATIC = Path(__file__).parent / "static"


# ---------- FRONT-END ----------
@app.get("/", include_in_schema=False)
def pagina_inicial():
    """Tela de cadastro (HTML + JS) que consome a própria API."""
    return FileResponse(PASTA_STATIC / "index.html")


@app.get("/simulador", include_in_schema=False)
def pagina_simulador():
    """Tela que mostra o input (requisição) e o output (resposta) de cada operação."""
    return FileResponse(PASTA_STATIC / "simulador.html")


def buscar_ou_404(db: Session, equipamento_id: int) -> Equipamento:
    equipamento = db.get(Equipamento, equipamento_id)
    if equipamento is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipamento não encontrado")
    return equipamento


def garantir_tag_unica(db: Session, tag: str, ignorar_id: int | None = None) -> None:
    existente = db.scalar(select(Equipamento).where(Equipamento.tag == tag))
    if existente and existente.id != ignorar_id:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Tag '{tag}' já cadastrada")


# ---------- CREATE ----------
@app.post("/equipamentos", response_model=EquipamentoSaida, status_code=status.HTTP_201_CREATED)
def criar(dados: EquipamentoCriar, db: Session = Depends(get_db)):
    garantir_tag_unica(db, dados.tag)
    equipamento = Equipamento(**dados.model_dump())
    db.add(equipamento)
    db.commit()
    db.refresh(equipamento)  # recarrega id e criado_em gerados pelo banco
    return equipamento


# ---------- READ (lista, com filtro e paginação) ----------
@app.get("/equipamentos", response_model=list[EquipamentoSaida])
def listar(
    status_: str | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = select(Equipamento).order_by(Equipamento.id)
    if status_:
        consulta = consulta.where(Equipamento.status == status_)
    return db.scalars(consulta.offset(skip).limit(limit)).all()


# ---------- READ (um só) ----------
@app.get("/equipamentos/{equipamento_id}", response_model=EquipamentoSaida)
def obter(equipamento_id: int, db: Session = Depends(get_db)):
    return buscar_ou_404(db, equipamento_id)


# ---------- UPDATE (parcial) ----------
@app.patch("/equipamentos/{equipamento_id}", response_model=EquipamentoSaida)
def atualizar(equipamento_id: int, dados: EquipamentoAtualizar, db: Session = Depends(get_db)):
    equipamento = buscar_ou_404(db, equipamento_id)
    mudancas = dados.model_dump(exclude_unset=True)  # só o que o cliente enviou
    if "tag" in mudancas:
        garantir_tag_unica(db, mudancas["tag"], ignorar_id=equipamento_id)
    for campo, valor in mudancas.items():
        setattr(equipamento, campo, valor)
    db.commit()
    db.refresh(equipamento)
    return equipamento


# ---------- DELETE ----------
@app.delete("/equipamentos/{equipamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(equipamento_id: int, db: Session = Depends(get_db)):
    equipamento = buscar_ou_404(db, equipamento_id)
    db.delete(equipamento)
    db.commit()
